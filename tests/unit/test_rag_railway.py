#!/usr/bin/env python3
"""
Test script for validating the RAG system on Railway deployment.

This script tests various aspects of the RAG system:
1. Basic RAG insights
2. Time-weighted retrieval
3. Different personas
4. Error handling

Usage:
    python test_rag_railway.py --base-url https://crave-trinity-backend-production.up.railway.app --token YOUR_AUTH_TOKEN
"""

import argparse
import json
import time
import sys
from datetime import datetime
import requests
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import track

# Initialize rich console
console = Console()

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Test RAG system on Railway")
    parser.add_argument("--base-url", required=True, help="Base URL of the deployment")
    parser.add_argument("--token", required=True, help="Authentication token")
    parser.add_argument("--outfile", default="rag_test_results.json", help="Output file for results")
    parser.add_argument("--verbose", action="store_true", help="Show detailed output")
    return parser.parse_args()

def get_auth_headers(token):
    """Get headers with authentication token."""
    return {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }

def test_personas(base_url, headers):
    """Test listing available personas."""
    console.print("[bold blue]Testing available personas...[/bold blue]")
    
    response = requests.get(f"{base_url}/api/ai/personas", headers=headers)
    
    if response.status_code == 200:
        personas = response.json().get("personas", [])
        
        table = Table(title="Available Personas")
        table.add_column("Persona")
        
        for persona in personas:
            table.add_row(persona)
            
        console.print(table)
        return personas
    else:
        console.print(f"[bold red]Error fetching personas: {response.status_code}[/bold red]")
        console.print(response.text)
        return []

def test_rag_insights(base_url, headers, personas):
    """Test RAG insights with various queries and configurations."""
    console.print("\n[bold blue]Testing RAG insights...[/bold blue]")
    
    # Define test cases
    test_cases = [
        {
            "title": "Basic query",
            "request": {
                "query": "Why do I crave sugary foods?",
                "top_k": 3,
                "time_weighted": True
            }
        },
        {
            "title": "Time-based query",
            "request": {
                "query": "Have my cravings changed over time?",
                "top_k": 5,
                "time_weighted": True
            }
        },
        {
            "title": "Non-time-weighted query",
            "request": {
                "query": "What are my strongest cravings?",
                "top_k": 3,
                "time_weighted": False
            }
        }
    ]
    
    # Add persona-specific test cases if personas are available
    for persona in personas:
        test_cases.append({
            "title": f"Query with {persona} persona",
            "request": {
                "query": "What can I do about my cravings?",
                "persona": persona,
                "top_k": 3
            }
        })
    
    # Run test cases
    results = []
    
    for case in track(test_cases, description="Running test cases"):
        start_time = time.time()
        
        try:
            response = requests.post(
                f"{base_url}/api/ai/rag/insights",
                headers=headers,
                json=case["request"],
                timeout=60  # Allow up to 60 seconds for response
            )
            
            elapsed = time.time() - start_time
            status = response.status_code
            
            result = {
                "title": case["title"],
                "request": case["request"],
                "status_code": status,
                "time_seconds": round(elapsed, 2)
            }
            
            if status == 200:
                result["answer"] = response.json().get("answer", "")
                result["success"] = True
            else:
                result["error"] = response.text
                result["success"] = False
                
            results.append(result)
            
            # Print result
            if result["success"]:
                console.print(f"✅ [green]{case['title']}: {status} in {elapsed:.2f}s[/green]")
                if args.verbose:
                    panel = Panel(
                        result["answer"], 
                        title=f"Response for '{case['request']['query']}'",
                        border_style="green"
                    )
                    console.print(panel)
            else:
                console.print(f"❌ [red]{case['title']}: {status} in {elapsed:.2f}s[/red]")
                console.print(f"[red]Error: {result['error']}[/red]")
                
        except Exception as e:
            console.print(f"❌ [red]{case['title']}: Exception: {str(e)}[/red]")
            results.append({
                "title": case["title"],
                "request": case["request"],
                "error": str(e),
                "success": False
            })
    
    return results

def test_error_handling(base_url, headers):
    """Test error handling with invalid requests."""
    console.print("\n[bold blue]Testing error handling...[/bold blue]")
    
    test_cases = [
        {
            "title": "Empty query",
            "request": {
                "query": "",
                "top_k": 3
            }
        },
        {
            "title": "Non-existent persona",
            "request": {
                "query": "Help with cravings",
                "persona": "NonExistentPersona123",
                "top_k": 3
            }
        },
        {
            "title": "Invalid top_k",
            "request": {
                "query": "Help with cravings",
                "top_k": -5
            }
        }
    ]
    
    results = []
    
    for case in test_cases:
        try:
            response = requests.post(
                f"{base_url}/api/ai/rag/insights",
                headers=headers,
                json=case["request"],
                timeout=30
            )
            
            if response.status_code != 200:
                console.print(f"✅ [green]{case['title']}: Expected error {response.status_code}[/green]")
            else:
                console.print(f"❌ [red]{case['title']}: Expected error but got 200 OK[/red]")
                
            results.append({
                "title": case["title"],
                "request": case["request"],
                "status_code": response.status_code,
                "response": response.text
            })
            
        except Exception as e:
            console.print(f"❌ [red]{case['title']}: Exception: {str(e)}[/red]")
            results.append({
                "title": case["title"],
                "request": case["request"],
                "error": str(e)
            })
    
    return results

def run_tests(args):
    """Run all tests."""
    base_url = args.base_url.rstrip("/")
    headers = get_auth_headers(args.token)
    
    console.print(Panel(f"Testing RAG on {base_url}", style="bold blue"))
    
    start_time = time.time()
    
    try:
        # Test available personas
        personas = test_personas(base_url, headers)
        
        # Test RAG insights
        insight_results = test_rag_insights(base_url, headers, personas)
        
        # Test error handling
        error_results = test_error_handling(base_url, headers)
        
        # Compile all results
        all_results = {
            "timestamp": datetime.now().isoformat(),
            "base_url": base_url,
            "personas": personas,
            "insight_tests": insight_results,
            "error_tests": error_results,
            "total_time_seconds": round(time.time() - start_time, 2)
        }
        
        # Save results
        with open(args.outfile, "w") as f:
            json.dump(all_results, f, indent=2)
            
        console.print(f"\n[bold green]Tests completed in {all_results['total_time_seconds']}s[/bold green]")
        console.print(f"Results saved to {args.outfile}")
        
        # Print summary
        success_count = sum(1 for test in insight_results if test.get("success", False))
        table = Table(title="Test Summary")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Total Tests", str(len(insight_results)))
        table.add_row("Successful Tests", str(success_count))
        table.add_row("Failed Tests", str(len(insight_results) - success_count))
        table.add_row("Success Rate", f"{(success_count / len(insight_results) * 100):.1f}%")
        table.add_row("Total Time", f"{all_results['total_time_seconds']}s")
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[bold red]Error during testing: {str(e)}[/bold red]")
        return 1
        
    return 0

if __name__ == "__main__":
    args = parse_args()
    sys.exit(run_tests(args))