#!/usr/bin/env python3
import subprocess
import time
import os
import glob
import re
import signal

# --- Settings ---
BASE_DIR = os.path.abspath(os.path.expanduser("~/Documents/Coding_C++"))
TEST_DIR = os.path.join(BASE_DIR, "Tests")
OUT_DIR = os.path.join(BASE_DIR, "Output")
DEATH_LOG = os.path.join(OUT_DIR, "death_toll.txt")
WHICHFILE = "coding.cpp"
os.makedirs(OUT_DIR, exist_ok=True)

TIME_LIMIT = 1.0 

def increment_death_toll():
    """Silently increments the persistent casualty counter."""
    count = 0
    if os.path.exists(DEATH_LOG):
        with open(DEATH_LOG, 'r') as f:
            try:
                line = f.read().strip()
                count = int(line) if line else 0
            except:
                count = 0
    count += 1
    with open(DEATH_LOG, 'w') as f:
        f.write(str(count))
    return count

def get_total_deaths():
    """Reads the current death toll without incrementing it."""
    if os.path.exists(DEATH_LOG):
        with open(DEATH_LOG, 'r') as f:
            try: return f.read().strip()
            except: return "0"
    return "0"

def get_critical_compiler_error(stderr_text):
    lines = stderr_text.splitlines()
    for i, line in enumerate(lines):
        if ": error:" in line:
            error_report = [line.strip()]
            for j in range(i + 1, min(i + 5, len(lines))):
                if "^" in lines[j] or "~" in lines[j]:
                    error_report.append(lines[j-1].strip()) 
                    error_report.append(lines[j].strip())  
                    break
            return "\n   ".join(error_report)
    return stderr_text.strip()

def get_crash_reason(return_code, stderr_msg):
    # Still incrementing the log file, but not printing it yet
    increment_death_toll()
    
    if "std::bad_alloc" in stderr_msg: return "OUT OF MEMORY"
    if "std::out_of_range" in stderr_msg: return "OUT OF RANGE"
    
    if return_code < 0:
        signum = abs(return_code)
        if signum == signal.SIGSEGV:
            return "SEGMENTATION FAULT"
       
        mapping = {
            signal.SIGFPE:  "FLOATING POINT ERROR",
            signal.SIGABRT: "ABORTED (Assertion/Corruption)",
            signal.SIGILL:  "ILLEGAL INSTRUCTION",
        }
        return mapping.get(signum, f"SIGNAL {signum}")
    
    return f"EXIT CODE {return_code}"

def get_peak_rss_kb(pid):
    try:
        with open(f"/proc/{pid}/status", "r") as f:
            content = f.read()
            match = re.search(r"VmHWM:\s+(\d+)\s+kB", content)
            if match: return int(match.group(1))
    except: return 0
    return 0

def run_tests():
    cpp_file = os.path.join(BASE_DIR, WHICHFILE)
    exe_file = os.path.join(OUT_DIR, "solution")
    
    print(f"Compiling {os.path.basename(cpp_file)}...")
    compile_proc = subprocess.run(["g++", "-O3", cpp_file, "-o", exe_file], capture_output=True, text=True)
    
    if compile_proc.returncode != 0:
        print("\033[1;31m[!] COMPILATION FAILED\033[0m")
        print(f"\033[1;33mCritical Problem:\033[0m\n   {get_critical_compiler_error(compile_proc.stderr)}")
        return

    inputs = sorted(glob.glob(os.path.join(TEST_DIR, "input*.txt")))
    passed = 0

    for input_path in inputs:
        input_file = os.path.basename(input_path)
        expected_path = input_path.replace("input", "expected")
        peak_kb = 0 
        
        with open(input_path, 'r') as infile:
            start_time = time.perf_counter()
            proc = subprocess.Popen([exe_file], stdin=infile, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
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
                    reason = get_crash_reason(proc.returncode, stderr_data)
                    print(f"\033[31m💥 CRASH: {input_file} | {reason}\033[0m")
                    continue

                with open(expected_path, 'r') as f: expected = f.read().strip()
                actual = stdout_data.strip()
                
                if actual == expected:
                    print(f"\033[32m✅ {input_file}: PASS \033[36m({runtime_ms}ms - {actual_mem_mb:.2f} MB)\033[0m")
                    passed += 1
                else:
                    print(f"\033[31m❌ {input_file}: FAIL \033[36m({runtime_ms}ms - {actual_mem_mb:.2f} MB)\033[0m")
                    print("-" * 40)
                    print(f"\033[1;34m[Expected]\033[0m\n{expected}")
                    print(f"\033[1;35m[Your Output]\033[0m\n{actual if actual else '<<nothing>>'}")
                    print("-" * 40)

            except subprocess.TimeoutExpired:
                print(f"\033[33m⏳ TLE: {input_file} > {TIME_LIMIT}s\033[0m")

    # Final Report Section
    total_deaths = get_total_deaths()
    print("\n" + "="*40)
    print(f"\033[1mScore: {passed}/{len(inputs)} tests passed\033[0m")
    print(f"\033[1;41m 💀 CAREER DEATH TOLL: {total_deaths} 💀 \033[0m")
    print("="*40)

if __name__ == "__main__":
    run_tests()
