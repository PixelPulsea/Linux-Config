#!/usr/bin/env python3
import subprocess
import time
import os
import glob
import re
import signal
import tempfile

# --- Settings ---
BASE_DIR = os.path.abspath(os.path.expanduser("~/Documents/Coding_C++"))
TEST_DIR = os.path.join(BASE_DIR, "Tests")
OUT_DIR = os.path.join(BASE_DIR, "Output")
DEATH_LOG = os.path.join(OUT_DIR, "death_toll.txt")
WHICHFILE = "coding.cpp"
os.makedirs(OUT_DIR, exist_ok=True)

TIME_LIMIT = 1.0

def truncate_output(text, max_lines=10):
    lines = text.splitlines()
    if len(lines) > max_lines:
        return "\n".join(lines[:max_lines]) + "\n..."
    return text

def increment_death_toll():
    count = 0
    if os.path.exists(DEATH_LOG):
        with open(DEATH_LOG, 'r') as f:
            try:
                line = f.read().strip()
                count = int(line) if line else 0
            except: count = 0
    count += 1
    with open(DEATH_LOG, 'w') as f:
        f.write(str(count))
    return count

def get_total_deaths():
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
            return "\n    ".join(error_report)
    return stderr_text.strip()

def get_crash_reason(return_code, stderr_msg):
    increment_death_toll() # Still count it!
    if "std::bad_alloc" in stderr_msg: return "OUT OF MEMORY"
    if "std::out_of_range" in stderr_msg: return "OUT OF RANGE"
    if return_code == 139:
        return "SEGMENTATION FAULT"
    if return_code < 0:
        signum = abs(return_code)
        if signum == signal.SIGSEGV: return "SEGMENTATION FAULT"
        mapping = {
            signal.SIGFPE:  "FLOATING POINT ERROR",
            signal.SIGABRT: "ABORTED (Assertion/Corruption)",
            signal.SIGILL:  "ILLEGAL INSTRUCTION",
        }
        return mapping.get(signum, f"SIGNAL {signum}")
    return f"EXIT CODE {return_code}"

def run_tests():
    cpp_file = os.path.join(BASE_DIR, WHICHFILE)
    exe_file = os.path.join(OUT_DIR, "solution")
    
    print(f"Compiling {os.path.basename(cpp_file)}...")
    compile_proc = subprocess.run(["g++", "-O3", "-march=native", cpp_file, "-o", exe_file], capture_output=True, text=True)
    
    if compile_proc.returncode != 0:
        print("\033[1;31m[!] COMPILATION FAILED\033[0m")
        print(f"\033[1;33mCritical Problem:\033[0m\n    {get_critical_compiler_error(compile_proc.stderr)}")
        return

    inputs = sorted(glob.glob(os.path.join(TEST_DIR, "input*.txt")))
    passed = 0
    had_crash = False

    for input_path in inputs:
        input_file = os.path.basename(input_path)
        expected_path = input_path.replace("input", "expected")
        
        with open(input_path, 'r') as infile, tempfile.NamedTemporaryFile(mode='r+') as mem_log:
            start_time = time.perf_counter()
            cmd = ["env", "time", "-f", "%M", "-o", mem_log.name, exe_file]
            
            proc = subprocess.Popen(cmd, stdin=infile, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            try:
                stdout_data, stderr_data = proc.communicate(timeout=TIME_LIMIT)
                runtime_ms = int((time.perf_counter() - start_time) * 1000)
                
                mem_log.seek(0)
                mem_str = mem_log.read().strip()
                peak_kb = int(mem_str) if mem_str.isdigit() else 0
                actual_mem_mb = peak_kb / 1024.0

                if proc.returncode != 0:
                    had_crash = True
                    reason = get_crash_reason(proc.returncode, stderr_data)
                    print(f"\033[31m💥 CRASH: {input_file}\n==== {reason} ====\033[0m")

                    continue

                with open(expected_path, 'r') as f: expected = f.read()
                actual = stdout_data
                
                # --- TOKENS ---
                exp_tokens = expected.split()
                act_tokens = actual.split()
                
                if exp_tokens == act_tokens: 
                    print("-" * 40)
                    print(f"\033[32m✅ {input_file}: PASS \033[36m({runtime_ms}ms - {actual_mem_mb:.2f} MB)\033[0m")
                    passed += 1
                else:
                    # If it's a logical fail, we still increment death toll
                    print("-" * 40)
                    print(f"\033[31m❌ {input_file}: FAIL \033[36m({runtime_ms}ms - {actual_mem_mb:.2f} MB)\033[0m")
                    
                    # FIND THE FIRST DIFFERENCE
                    diff_idx = -1
                    for i in range(min(len(exp_tokens), len(act_tokens))):
                        if exp_tokens[i] != act_tokens[i]:
                            diff_idx = i
                            break
                    
                    if diff_idx != -1:
                        print(f"\033[1;31m[Mismatch at word {diff_idx+1}]\033[0m")
                        print(f"Expected: '{exp_tokens[diff_idx]}'")
                        print(f"Actual:   '{act_tokens[diff_idx]}'")
                    
                    if len(exp_tokens) != len(act_tokens):
                        print(f"\033[1;31m[Count Mismatch]\033[0m\nExpected {len(exp_tokens)} words, got {len(act_tokens)}")
                        
                    print(f"\033[1;34m[Expected]\033[0m\n{truncate_output(expected.strip(), 10)}")
                    print(f"\033[1;35m[Your Output]\033[0m\n{truncate_output(actual.strip(), 10) if actual else '<<nothing>>'}")

            except subprocess.TimeoutExpired:
                had_crash = True
                increment_death_toll()
                proc.kill()
                proc.wait()
                print(f"\033[33m⏳ TLE: {input_file} > {TIME_LIMIT}s\033[0m")

    # --- FINAL REVEAL ---
    total_deaths = get_total_deaths()
    print("="*40)
    print(f"\033[1mScore: {passed}/{len(inputs)} tests passed\033[0m")
    
    if had_crash:
        # Dramatic red banner only on failure/crash
        print(f"\033[1;41m TOTAL CRASH TOLL: {total_deaths} \033[0m")
    if passed == len(inputs):
        print(f"\033[1;32m🌟 PERFECTION: GOOD JOB, NOW TEST SOME EDGE CASES 🌟\033[0m")
        
    print("="*40)

if __name__ == "__main__":
    run_tests()
