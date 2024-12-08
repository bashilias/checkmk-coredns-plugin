#!/usr/bin/env python3

'''
    CoreDNS Plugin v0.1
    Copyright 2024 Ilias

    CheckMK plugin for checking error's in CoreDNS pods.
    Kubectl is needed on host for the plugin to work.
'''
import subprocess
import sys

# Threshold for warning
ERROR_THRESHOLD = 10

def fetch_coredns_logs():
    try:
        result = subprocess.run(
            ["kubectl", "logs", "-n", "kube-system", "-l", "k8s-app=kube-dns", "--tail", "100"],
            stdout=subprocess.PIPE, # stdout captured
            stderr=subprocess.PIPE, # error during executing captured
            universal_newlines=True 
        )
        if result.returncode != 0: # if rreturn code not 0 print stdout of executed kubectl command
            print(f"Error fetching logs: {result.stderr}")
            sys.exit(1) # exit script with status 1 instead of 0
        return result.stdout # else return stdout of executed kubectl command
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

def count_errors(logs):
    totalErrors = 0
    for line in logs.splitlines():
        if "[ERROR]" in line:
            totalErrors =+1
            if totalErrors == 1000:
                return totalErrors # stop count at 1000 to increase performance
    return totalErrors # counting and returning total error lines

def generate_output(error_count):

    if error_count >= ERROR_THRESHOLD: # if total error lines >= the threshold print erros
        # WARNING status
        print(f"1 CoreDNS errors={error_count} WARNING - {error_count} errors found")
    else:
        # OK status
        print(f"0 CoreDNS errors={error_count} OK - {error_count} errors found")

def main():
    logs = fetch_coredns_logs()
    error_count = count_errors(logs)
    generate_output(error_count)

main()
