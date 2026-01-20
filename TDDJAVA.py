#!/usr/bin/env python3
import subprocess
import time
import os
import glob
import re
import signal

# --- Settings ---
# Note: In Java, the class name must match the filename. 
# This script assumes your file is named 'coding.java' and contains 'public class coding'
BASE_DIR = os.path.abspath(os.path.expanduser("~/Documents/Java/Personal"))
TEST_DIR = os.path.join(BASE_DIR, "Tests")
OUT_DIR = os.path.join(BASE_DIR, "Output")
os.makedirs(OUT_DIR, exist_ok=True)
WHICHFILE = "calculator.java"
CLASSNAME = "calculator"

TIME_LIMIT = 1.0 

def get_critical_java_error(stderr_text):
    """Parses javac output to find the first error and the code pointer."""
    lines = stderr_text.splitlines()
    for i, line in enumerate(lines):
        if " error:" in line.lower():
            error_report = [line.strip()]
            # javac usually shows the code line and the '^' in the next 2 lines
            if i + 2 < len(lines):
                error_report.append(lines[i+1].strip())
                error_report.append(lines[i+2].strip())
            return "\n   ".join(error_report)
    return stderr_text.strip()

def get_java_crash_reason(return_code, stderr_msg):
    """Translates Java Exceptions into your C++ style reasons."""
    if "java.lang.OutOfMemoryError" in stderr_msg:
        return "OUT OF MEMORY (Heap/Stack Limit)"
    if "ArrayIndexOutOfBoundsException" in stderr_msg:
        return "OUT OF RANGE (Array Index Error)"
    if "NullPointerException" in stderr_msg:
        return "SEGMENTATION FAULT"
    if "ArithmeticException: / by zero" in stderr_msg:
        return "FLOATING POINT ERROR (Div by 0)"
    if "StackOverflowError" in stderr_msg:
        return "STACK OVERFLOW (Recursion too deep)"
    
    return f"RUNTIME ERROR (Exit Code: {return_code})"

def get_peak_rss_kb(pid):
    try:
        with open(f"/proc/{pid}/status", "r") as f:
            content = f.read()
            match = re.search(r"VmHWM:\s+(\d+)\s+kB", content)
            if match: return int(match.group(1))
    except: return 0
    return 0

def run_tests():
    java_file = os.path.join(BASE_DIR, WHICHFILE)
    class_name = CLASSNAME # Name of the class to run
    
    if not os.path.exists(java_file):
        print(f"Error: {java_file} not found.")
        return

    print(f"Compiling {os.path.basename(java_file)}...")
    # Compile step: javac
    compile_proc = subprocess.run(["javac", "-d", OUT_DIR, java_file], capture_output=True, text=True)
    
    if compile_proc.returncode != 0:
        print(f"\033[1;31m[!] COMPILATION FAILED (Exit Code: {compile_proc.returncode})\033[0m")
        error_msg = get_critical_java_error(compile_proc.stderr)
        print(f"\033[1;33mCritical Problem:\033[0m\n   {error_msg}")
        return

    inputs = sorted(glob.glob(os.path.join(TEST_DIR, "input*.txt")))
    passed = 0

    for input_path in inputs:
        input_file = os.path.basename(input_path)
        expected_path = input_path.replace("input", "expected")
        peak_kb = 0 
        
        with open(input_path, 'r') as infile:
            start_time = time.perf_counter()
            # Run step: java -cp (classpath) class_name
            proc = subprocess.Popen(
                ["java", "-cp", OUT_DIR, class_name], 
                stdin=infile, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            
            try:
                while proc.poll() is None:
                    peak_kb = max(peak_kb, get_peak_rss_kb(proc.pid))
                    if (time.perf_counter() - start_time) > TIME_LIMIT:
                        proc.kill()
                        raise subprocess.TimeoutExpired(proc.args, TIME_LIMIT)
                    time.sleep(0.001) 
                
                stdout_data, stderr_data = proc.communicate()
                runtime_ms = int((time.perf_counter() - start_time) * 1000)
                actual_mem_mb = peak_kb / 1024.0

                if proc.returncode != 0:
                    reason = get_java_crash_reason(proc.returncode, stderr_data)
                    print(f"\033[31m💥 CRASH: {input_file} | {reason}\033[0m")
                    continue

                with open(expected_path, 'r') as f: expected = f.read().strip()
                actual = stdout_data.strip()
                
                if actual == expected:
                    print(f"\033[32m✅ {input_file}: PASS \033[36m({runtime_ms}ms - {actual_mem_mb:.2f} MB)\033[0m")
                    print("-" * 40)
                    passed += 1
                else:
                    print("-" * 40)
                    print(f"\033[31m❌ {input_file}: FAIL \033[36m({runtime_ms}ms - {actual_mem_mb:.2f} MB)\033[0m")
                    print(f"\033[1;34m[Expected]\033[0m\n{expected}")
                    print(f"\033[1;35m[Your Output]\033[0m\n{actual if actual else '<<nothing>>'}")
                    print("-" * 40)

            except subprocess.TimeoutExpired:
                print(f"\033[33m⏳ TLE: {input_file}\033[0m")

    print(f"\n\033[1mScore: {passed}/{len(inputs)} tests passed\033[0m")

if __name__ == "__main__":
    run_tests()
