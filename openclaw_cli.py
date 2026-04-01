"""
OpenClaw Command-Line Interface
Professional CLI tool for automation, browser control, and bot management
"""

import json
import asyncio
import click
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from tabulate import tabulate

from automation_skills import AutomationSkills
from browser_controller import BrowserControllerFactory

logger = logging.getLogger(__name__)

skills_lib = AutomationSkills()


class CLIContext:
    """CLI context for maintaining state"""
    def __init__(self):
        self.current_session = None
        self.controller = BrowserControllerFactory.get_controller()
        self.verbose = False


@click.group()
@click.option('--verbose', is_flag=True, help='Enable verbose output')
@click.pass_context
def cli(ctx, verbose):
    """OpenClaw - Professional Web Automation CLI"""
    ctx.ensure_object(dict)
    ctx.obj['cli'] = CLIContext()
    ctx.obj['cli'].verbose = verbose
    if verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)


# ============= SKILLS COMMANDS =============

@cli.group()
def skills():
    """Manage automation skills"""
    pass


@skills.command()
@click.pass_context
def list(ctx):
    """List all available skills"""
    skills_list = skills_lib.list_all_skills()
    
    # Group by category
    by_category = {}
    for skill in skills_list:
        cat = skill['category']
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(skill)
    
    # Display in table format
    for category, cat_skills in sorted(by_category.items()):
        click.echo(f"\n{click.style(category.upper(), fg='cyan', bold=True)}")
        table_data = [
            [s['id'], s['name'], s['difficulty']]
            for s in cat_skills
        ]
        click.echo(tabulate(table_data, headers=['ID', 'Name', 'Difficulty'], tablefmt='grid'))
    
    click.echo(f"\n{click.style(f'Total: {len(skills_list)} skills', fg='green', bold=True)}")


@skills.command()
@click.argument('skill_id')
@click.option('--json', is_flag=True, help='Output as JSON')
@click.pass_context
def info(ctx, skill_id, json_output):
    """Get detailed skill information"""
    skill = skills_lib.get_skill(skill_id)
    
    if not skill:
        click.echo(click.style(f"Error: Skill '{skill_id}' not found", fg='red'), err=True)
        return
    
    if json_output:
        click.echo(json.dumps({
            'id': skill.id,
            'name': skill.name,
            'description': skill.description,
            'category': skill.category,
            'parameters': skill.parameters,
            'difficulty': skill.difficulty,
            'tags': skill.tags
        }, indent=2))
    else:
        click.echo(f"\n{click.style(skill.name, fg='cyan', bold=True)}")
        click.echo(f"ID: {skill.id}")
        click.echo(f"Category: {skill.category}")
        click.echo(f"Difficulty: {click.style(skill.difficulty, fg='yellow')}")
        click.echo(f"Description: {skill.description}")
        click.echo(f"Tags: {', '.join(skill.tags)}")
        click.echo(f"Timeout: {skill.timeout_seconds}s")
        click.echo(f"Retries: {skill.retry_count}")


@skills.command()
@click.option('--category', help='Filter by category')
@click.option('--tag', help='Filter by tag')
@click.option('--json', is_flag=True, help='Output as JSON')
@click.pass_context
def search(ctx, category, tag, json_output):
    """Search for skills"""
    if category:
        results = skills_lib.get_skills_by_category(category)
    elif tag:
        results = skills_lib.get_skills_by_tag(tag)
    else:
        results = list(skills_lib.skills.values())
    
    if json_output:
        click.echo(json.dumps([{
            'id': s.id,
            'name': s.name,
            'category': s.category
        } for s in results], indent=2))
    else:
        if not results:
            click.echo("No skills found")
            return
        
        table_data = [[s.id, s.name, s.category] for s in results]
        click.echo(tabulate(table_data, headers=['ID', 'Name', 'Category'], tablefmt='grid'))
        click.echo(f"\nFound: {len(results)} skills")


# ============= BROWSER COMMANDS =============

@cli.group()
def browser():
    """Control browser and sessions"""
    pass


@browser.command()
@click.option('--headless/--headed', default=True, help='Run in headless mode')
@click.pass_context
async def session(ctx, headless):
    """Create a browser session"""
    cli_ctx = ctx.obj['cli']
    controller = cli_ctx.controller
    
    session_id = f"session_{datetime.now().timestamp()}"
    session = await controller.create_session(session_id)
    
    cli_ctx.current_session = session_id
    
    click.echo(click.style(f"✓ Session created: {session_id}", fg='green', bold=True))
    click.echo(f"Headless: {headless}")
    click.echo(f"Created: {session.created_at}")


@browser.command()
@click.pass_context
def list_sessions(ctx):
    """List active sessions"""
    cli_ctx = ctx.obj['cli']
    sessions = cli_ctx.controller.sessions
    
    if not sessions:
        click.echo("No active sessions")
        return
    
    table_data = [
        [sid, s.created_at, s.url or 'N/A']
        for sid, s in sessions.items()
    ]
    click.echo(tabulate(table_data, headers=['Session ID', 'Created', 'URL'], tablefmt='grid'))


@browser.command()
@click.argument('url')
@click.option('--session', help='Session ID (uses current if not specified)')
@click.pass_context
async def navigate(ctx, url, session):
    """Navigate to URL"""
    cli_ctx = ctx.obj['cli']
    session_id = session or cli_ctx.current_session
    
    if not session_id:
        click.echo(click.style("Error: No session specified", fg='red'), err=True)
        return
    
    result = await cli_ctx.controller.navigate(session_id, url)
    if result['status'] == 'success':
        click.echo(click.style(f"✓ Navigated to {url}", fg='green'))
    else:
        click.echo(click.style(f"✗ Navigation failed: {result.get('message')}", fg='red'), err=True)


# ============= AUTOMATION COMMANDS =============

@cli.group()
def automation():
    """Run automation tasks"""
    pass


@automation.command()
@click.argument('skill_id')
@click.argument('parameters', required=False, default='{}')
@click.option('--session', help='Session ID (uses current if not specified)')
@click.option('--json-out', is_flag=True, help='Output as JSON')
@click.pass_context
async def execute(ctx, skill_id, parameters, session, json_out):
    """Execute a skill"""
    cli_ctx = ctx.obj['cli']
    session_id = session or cli_ctx.current_session
    
    if not session_id:
        click.echo(click.style("Error: No session specified", fg='red'), err=True)
        return
    
    # Parse parameters
    try:
        params = json.loads(parameters)
    except json.JSONDecodeError:
        click.echo(click.style("Error: Invalid JSON parameters", fg='red'), err=True)
        return
    
    # Execute skill
    action = await cli_ctx.controller.execute_skill(session_id, skill_id, params)
    
    if json_out:
        click.echo(json.dumps({
            'action_id': action.action_id,
            'skill_id': action.skill_id,
            'status': action.status,
            'result': action.result,
            'error': action.error
        }, indent=2))
    else:
        if action.status == 'completed':
            click.echo(click.style(f"✓ Skill executed: {skill_id}", fg='green'))
            if action.result:
                click.echo(f"Result: {json.dumps(action.result, indent=2)}")
        else:
            click.echo(click.style(f"✗ Skill failed: {action.error}", fg='red'), err=True)


@automation.command()
@click.argument('workflow_file')
@click.option('--session', help='Session ID (uses current if not specified)')
@click.pass_context
async def run_workflow(ctx, workflow_file, session):
    """Run a workflow from JSON file"""
    cli_ctx = ctx.obj['cli']
    session_id = session or cli_ctx.current_session
    
    if not session_id:
        click.echo(click.style("Error: No session specified", fg='red'), err=True)
        return
    
    try:
        with open(workflow_file, 'r') as f:
            workflow = json.load(f)
    except FileNotFoundError:
        click.echo(click.style(f"Error: File not found: {workflow_file}", fg='red'), err=True)
        return
    except json.JSONDecodeError:
        click.echo(click.style(f"Error: Invalid JSON file", fg='red'), err=True)
        return
    
    click.echo(f"Running workflow with {len(workflow)} steps...")
    with click.progressbar(length=len(workflow)) as bar:
        result = await cli_ctx.controller.execute_workflow(session_id, workflow)
        bar.update(len(workflow))
    
    if result['status'] == 'success':
        click.echo(click.style(f"✓ Workflow completed: {result['total_steps']} steps", fg='green'))
    else:
        click.echo(click.style(f"✗ Workflow failed after {result['completed_steps']} steps", fg='red'), err=True)


@automation.command()
@click.option('--session', help='Session ID (uses current if not specified)')
@click.option('--limit', default=20, help='Number of actions to show')
@click.pass_context
def history(ctx, session, limit):
    """Show automation history"""
    cli_ctx = ctx.obj['cli']
    session_id = session or cli_ctx.current_session
    
    history_list = cli_ctx.controller.get_actions_history(session_id, limit)
    
    if not history_list:
        click.echo("No history available")
        return
    
    table_data = [
        [h['skill_id'], h['status'], h['timestamp']]
        for h in history_list
    ]
    click.echo(tabulate(table_data, headers=['Skill', 'Status', 'Timestamp'], tablefmt='grid'))


# ============= INFO COMMANDS =============

@cli.command()
def version():
    """Show version information"""
    click.echo(f"OpenClaw v1.0.0")
    click.echo(f"Skills: {len(skills_lib.skills)}")


@cli.command()
def status():
    """Show system status"""
    cli_ctx = click.get_current_context().obj.get('cli')
    sessions = cli_ctx.controller.sessions if cli_ctx else {}
    
    click.echo(f"Status: Operational")
    click.echo(f"Timestamp: {datetime.now().isoformat()}")
    click.echo(f"Total Skills: {len(skills_lib.skills)}")
    click.echo(f"Active Sessions: {len(sessions)}")


if __name__ == '__main__':
    cli(obj={})
