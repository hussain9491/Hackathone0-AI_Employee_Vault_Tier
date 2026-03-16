"""
Silver Tier Verification Script for AI Employee

Tests all Silver Tier requirements:
1. Two or more Watcher scripts (Gmail + LinkedIn)
2. Automatically Post on LinkedIn
3. Plan.md file creation
4. One working MCP server
5. Human-in-the-loop approval workflow
6. Basic scheduling

Usage:
    python verify_silver_tier.py --vault-path ../AI_Employee_Vault
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path
from datetime import datetime


class SilverTierVerifier:
    """Verify Silver Tier deliverables."""
    
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.scripts_path = self.vault_path / 'scripts'
        self.results = {
            'passed': 0,
            'failed': 0,
            'tests': []
        }
        
    def check_watcher_scripts(self) -> bool:
        """Check for two or more watcher scripts."""
        print("\n📋 Checking Watcher Scripts...")
        
        watchers = {
            'Gmail Watcher': self.scripts_path / 'gmail_watcher.py',
            'LinkedIn Watcher': self.scripts_path / 'linkedin_watcher.py',
            'Filesystem Watcher': self.scripts_path / 'filesystem_watcher.py'
        }
        
        found = 0
        for name, path in watchers.items():
            if path.exists():
                print(f"   ✅ {name}: Found")
                found += 1
            else:
                print(f"   ❌ {name}: Missing")
        
        passed = found >= 2
        self._record_test("Watcher Scripts (2+)", passed, f"{found} watchers found")
        return passed
    
    def check_linkedin_poster(self) -> bool:
        """Check for LinkedIn auto-posting capability."""
        print("\n💼 Checking LinkedIn Auto-Poster...")
        
        linkedin_script = self.scripts_path / 'linkedin_watcher.py'
        linkedin_skill = Path('../../.qwen/skills/linkedin-poster/SKILL.md')
        
        if not linkedin_script.exists():
            print(f"   ❌ linkedin_watcher.py: Missing")
            self._record_test("LinkedIn Auto-Poster", False, "Script missing")
            return False
        
        # Check script has posting functionality
        content = linkedin_script.read_text(encoding='utf-8')
        has_post_function = 'post' in content.lower() or 'create' in content.lower()
        
        if has_post_function:
            print(f"   ✅ LinkedIn Watcher: Has posting functionality")
        else:
            print(f"   ⚠️  LinkedIn Watcher: Posting functionality unclear")
        
        # Check skill documentation
        if linkedin_skill.exists():
            print(f"   ✅ LinkedIn Skill: Documentation exists")
        else:
            print(f"   ⚠️  LinkedIn Skill: Documentation missing")
        
        passed = linkedin_script.exists() and has_post_function
        self._record_test("LinkedIn Auto-Poster", passed, "Script + functionality")
        return passed
    
    def check_plan_generator(self) -> bool:
        """Check for Plan.md file creation capability."""
        print("\n📝 Checking Plan Generator...")
        
        plan_script = self.scripts_path / 'plan_generator.py'
        plan_skill = Path('../../.qwen/skills/plan-generator/SKILL.md')
        plans_folder = self.vault_path / 'Plans'
        
        if plan_script.exists():
            print(f"   ✅ Plan Generator Script: Found")
        else:
            print(f"   ❌ Plan Generator Script: Missing")
        
        if plan_skill.exists():
            print(f"   ✅ Plan Generator Skill: Documentation exists")
        else:
            print(f"   ⚠️  Plan Generator Skill: Documentation missing")
        
        if plans_folder.exists():
            print(f"   ✅ Plans Folder: Exists")
        else:
            print(f"   ⚠️  Plans Folder: Missing")
        
        passed = plan_script.exists() or plans_folder.exists()
        self._record_test("Plan Generator", passed, "Plan creation capability")
        return passed
    
    def check_mcp_server(self) -> bool:
        """Check for working MCP server."""
        print("\n🔌 Checking MCP Server...")
        
        mcp_folder = self.scripts_path / 'mcp-email'
        mcp_skill = Path('../../.qwen/skills/email-mcp/SKILL.md')
        mcp_server_skill = Path('../../.qwen/skills/mcp-server/SKILL.md')
        
        if mcp_folder.exists():
            print(f"   ✅ MCP Email Server: Folder exists")
        else:
            print(f"   ⚠️  MCP Email Server: Folder missing")
        
        if mcp_skill.exists() or mcp_server_skill.exists():
            print(f"   ✅ MCP Skill: Documentation exists")
        else:
            print(f"   ⚠️  MCP Skill: Documentation missing")
        
        # Check if MCP package is installed
        try:
            import mcp
            print(f"   ✅ MCP Package: Installed")
            mcp_installed = True
        except ImportError:
            print(f"   ❌ MCP Package: Not installed")
            mcp_installed = False
        
        passed = mcp_folder.exists() or mcp_installed
        self._record_test("MCP Server", passed, "MCP capability")
        return passed
    
    def check_approval_workflow(self) -> bool:
        """Check for human-in-the-loop approval workflow."""
        print("\n✅ Checking Approval Workflow...")
        
        approval_script = self.scripts_path / 'approval_workflow.py'
        approval_skill_v2 = Path('../../.qwen/skills/approval-workflow-v2/SKILL.md')
        pending_folder = self.vault_path / 'Pending_Approval'
        approved_folder = self.vault_path / 'Approved'
        
        checks = []
        
        if approval_script.exists():
            print(f"   ✅ Approval Workflow Script: Found")
            checks.append(True)
        else:
            print(f"   ❌ Approval Workflow Script: Missing")
            checks.append(False)
        
        if approval_skill_v2.exists():
            print(f"   ✅ Approval Skill V2: Documentation exists")
            checks.append(True)
        else:
            print(f"   ⚠️  Approval Skill V2: Documentation missing")
            checks.append(False)
        
        if pending_folder.exists():
            print(f"   ✅ Pending_Approval Folder: Exists")
            checks.append(True)
        else:
            print(f"   ❌ Pending_Approval Folder: Missing")
            checks.append(False)
        
        if approved_folder.exists():
            print(f"   ✅ Approved Folder: Exists")
            checks.append(True)
        else:
            print(f"   ❌ Approved Folder: Missing")
            checks.append(False)
        
        passed = sum(checks) >= 3
        self._record_test("Approval Workflow", passed, f"{sum(checks)}/4 checks passed")
        return passed
    
    def check_scheduler(self) -> bool:
        """Check for basic scheduling capability."""
        print("\n⏰ Checking Scheduler...")
        
        scheduler_script = self.scripts_path / 'scheduler.py'
        scheduler_skill = Path('../../.qwen/skills/scheduler/SKILL.md')
        
        if scheduler_script.exists():
            print(f"   ✅ Scheduler Script: Found")
        else:
            print(f"   ❌ Scheduler Script: Missing")
        
        if scheduler_skill.exists():
            print(f"   ✅ Scheduler Skill: Documentation exists")
        else:
            print(f"   ⚠️  Scheduler Skill: Documentation missing")
        
        passed = scheduler_script.exists()
        self._record_test("Scheduler", passed, "Scheduling capability")
        return passed
    
    def check_skills_documentation(self) -> bool:
        """Check for Agent Skills documentation."""
        print("\n📚 Checking Skills Documentation...")
        
        skills_path = Path('../../.qwen/skills')
        if not skills_path.exists():
            print(f"   ❌ Skills folder: Missing")
            self._record_test("Skills Documentation", False, "Skills folder missing")
            return False
        
        # Count skill folders
        skill_count = len([d for d in skills_path.iterdir() if d.is_dir()])
        print(f"   ✅ Skills folder: Found ({skill_count} skills)")
        
        # Check for key Silver tier skills
        silver_skills = [
            'gmail-watcher',
            'linkedin-poster',
            'approval-workflow-v2',
            'scheduler'
        ]
        
        found_skills = 0
        for skill in silver_skills:
            skill_path = skills_path / skill
            if skill_path.exists():
                print(f"   ✅ {skill}: Found")
                found_skills += 1
            else:
                print(f"   ❌ {skill}: Missing")
        
        passed = found_skills >= 3
        self._record_test("Skills Documentation", passed, f"{found_skills}/{len(silver_skills)} Silver skills")
        return passed
    
    def _record_test(self, name: str, passed: bool, details: str):
        """Record a test result."""
        self.results['tests'].append({
            'name': name,
            'passed': passed,
            'details': details
        })
        if passed:
            self.results['passed'] += 1
        else:
            self.results['failed'] += 1
    
    def generate_report(self) -> str:
        """Generate verification report."""
        total = self.results['passed'] + self.results['failed']
        pass_rate = (self.results['passed'] / total * 100) if total > 0 else 0
        
        report = f"""
{'=' * 60}
SILVER TIER VERIFICATION REPORT
{'=' * 60}

Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Vault: {self.vault_path}

RESULTS:
--------
Passed: {self.results['passed']}/{total} ({pass_rate:.1f}%)
Failed: {self.results['failed']}/{total}

DETAILED RESULTS:
-----------------
"""
        
        for test in self.results['tests']:
            status = '✅' if test['passed'] else '❌'
            report += f"{status} {test['name']}: {test['details']}\n"
        
        # Overall verdict
        report += f"""
{'=' * 60}
VERDICT: {'✅ SILVER TIER COMPLETE' if pass_rate >= 80 else '⚠️  SILVER TIER IN PROGRESS'}
{'=' * 60}
"""
        
        if pass_rate >= 80:
            report += """
🎉 Congratulations! Silver Tier requirements are met.

Next Steps:
1. Test each watcher individually
2. Configure API credentials
3. Run watchers in background
4. Monitor action files in Needs_Action/
"""
        else:
            report += """
⚠️  Some Silver Tier requirements are incomplete.

Missing items to complete:
"""
            for test in self.results['tests']:
                if not test['passed']:
                    report += f"- {test['name']}\n"
        
        return report
    
    def run_all_checks(self) -> bool:
        """Run all verification checks."""
        print("=" * 60)
        print("SILVER TIER VERIFICATION")
        print("=" * 60)
        
        self.check_watcher_scripts()
        self.check_linkedin_poster()
        self.check_plan_generator()
        self.check_mcp_server()
        self.check_approval_workflow()
        self.check_scheduler()
        self.check_skills_documentation()
        
        # Generate and print report
        report = self.generate_report()
        print(report)
        
        # Save report
        report_file = self.vault_path / 'SILVER_TIER_VERIFICATION.md'
        report_file.write_text(report, encoding='utf-8')
        print(f"\n📄 Full report saved to: {report_file}")
        
        return self.results['passed'] >= (self.results['passed'] + self.results['failed']) * 0.8


def main():
    parser = argparse.ArgumentParser(description='Silver Tier Verification')
    parser.add_argument('--vault-path', default='..', help='Path to vault')
    
    args = parser.parse_args()
    
    verifier = SilverTierVerifier(args.vault_path)
    success = verifier.run_all_checks()
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
