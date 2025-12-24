"""
Task Executor
Executes parsed tasks using appropriate plugins
"""

from typing import Dict, Optional, Any
from datetime import datetime
import json


class TaskExecutor:
    """Executes tasks using plugins"""

    def __init__(self, plugin_manager, activity_tracker=None, ai_assistant=None):
        self.plugin_manager = plugin_manager
        self.tracker = activity_tracker
        self.ai = ai_assistant
        self.task_history = []

    def execute(self, task_plan: Dict) -> Dict[str, Any]:
        """
        Execute a task plan

        Args:
            task_plan: Dict with 'plugin', 'action', 'params'

        Returns:
            Execution result
        """

        plugin_name = task_plan.get('plugin')
        action = task_plan.get('action')
        params = task_plan.get('params', {})

        # Get plugin
        plugin = self.plugin_manager.get_plugin(plugin_name)
        if not plugin:
            return {
                'success': False,
                'error': f"Plugin '{plugin_name}' not found"
            }

        # Log task start
        task_id = self._log_task_start(task_plan)

        try:
            # Execute action
            result = self._execute_action(plugin, action, params)

            # Log success
            self._log_task_complete(task_id, result)

            return {
                'success': True,
                'result': result,
                'task_id': task_id
            }

        except Exception as e:
            # Log failure
            self._log_task_error(task_id, str(e))

            return {
                'success': False,
                'error': str(e),
                'task_id': task_id
            }

    def _execute_action(self, plugin, action: str, params: Dict) -> Any:
        """Execute the actual action on the plugin"""

        # Standard actions
        if action == 'send_message':
            return plugin.send_message(
                recipient=params.get('recipient', params.get('to', '')),
                message=params.get('message', params.get('text', ''))
            )

        elif action == 'read_messages':
            limit = int(params.get('limit', 10))
            return plugin.read_messages(limit)

        elif action == 'search':
            query = params.get('query', params.get('search', ''))
            return plugin.search(query, **params)

        elif action == 'send_email':
            return plugin.send_email(
                to=params.get('to', params.get('recipient', '')),
                subject=params.get('subject', ''),
                body=params.get('body', params.get('message', ''))
            )

        elif action == 'get_unread_emails':
            limit = int(params.get('limit', 10))
            return plugin.get_unread_emails(limit)

        elif action == 'delete':
            items = params.get('items', [])
            if hasattr(plugin, 'delete_media'):
                return plugin.delete_media(items)
            elif hasattr(plugin, 'delete'):
                return plugin.delete(items)

        # Custom actions
        elif hasattr(plugin, 'execute_action'):
            return plugin.execute_action(action, **params)

        else:
            raise ValueError(f"Action '{action}' not supported by {plugin.name}")

    def execute_from_natural_language(self, task_description: str) -> Dict[str, Any]:
        """
        Parse and execute a task from natural language

        Args:
            task_description: Natural language task description

        Returns:
            Execution result
        """

        from .task_parser import TaskParser, TaskValidator

        # Parse task
        parser = TaskParser(self.ai)
        task_plan = parser.parse(task_description, self.plugin_manager.get_enabled_plugins())

        # Validate task
        is_valid, error = TaskValidator.validate(task_plan, self.plugin_manager)
        if not is_valid:
            return {
                'success': False,
                'error': error,
                'task_plan': task_plan
            }

        # Execute task
        return self.execute(task_plan)

    def execute_multi_step_task(self, task_description: str) -> Dict[str, Any]:
        """
        Execute a complex multi-step task

        Args:
            task_description: Natural language description of complex task

        Returns:
            Execution result with steps
        """

        if not self.ai:
            return {
                'success': False,
                'error': 'AI assistant required for multi-step tasks'
            }

        # Ask AI to break down task into steps
        prompt = f"""Zerlege folgende Aufgabe in einzelne Schritte:

Aufgabe: "{task_description}"

Gib die Schritte im folgenden Format zurück (ein Schritt pro Zeile):
STEP 1: [Plugin] - [Action] - [Params]
STEP 2: [Plugin] - [Action] - [Params]
...

Beispiel:
STEP 1: Slack - send_message - recipient=Max, message=Meeting um 15 Uhr
STEP 2: Mail - send_email - to=max@example.com, subject=Meeting, body=Bestätigung
"""

        response = self.ai.process_query(prompt)

        # Parse steps
        steps = self._parse_steps(response)

        # Execute steps
        results = []
        for i, step in enumerate(steps):
            print(f"Executing step {i+1}/{len(steps)}: {step}")

            result = self.execute(step)
            results.append(result)

            if not result['success']:
                return {
                    'success': False,
                    'error': f"Failed at step {i+1}",
                    'completed_steps': results
                }

        return {
            'success': True,
            'steps_executed': len(results),
            'results': results
        }

    def _parse_steps(self, ai_response: str) -> list[Dict]:
        """Parse AI response into step dictionaries"""
        import re

        steps = []
        lines = ai_response.split('\n')

        for line in lines:
            match = re.match(r'STEP \d+:\s*(\w+)\s*-\s*(\w+)\s*-\s*(.+)', line)
            if match:
                plugin, action, params_str = match.groups()

                # Parse params
                params = {}
                param_pairs = re.findall(r'(\w+)=([^,]+)', params_str)
                for key, value in param_pairs:
                    params[key.strip()] = value.strip()

                steps.append({
                    'plugin': plugin.strip(),
                    'action': action.strip(),
                    'params': params
                })

        return steps

    def _log_task_start(self, task_plan: Dict) -> str:
        """Log task start"""
        task_id = f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        task_entry = {
            'id': task_id,
            'plan': task_plan,
            'started_at': datetime.now().isoformat(),
            'status': 'running'
        }

        self.task_history.append(task_entry)

        if self.tracker:
            self.tracker.log_activity(
                app_name='TaskExecutor',
                activity_type='task_started',
                title=task_plan.get('action', 'Unknown'),
                content=json.dumps(task_plan)
            )

        return task_id

    def _log_task_complete(self, task_id: str, result: Any):
        """Log task completion"""
        for task in self.task_history:
            if task['id'] == task_id:
                task['status'] = 'completed'
                task['completed_at'] = datetime.now().isoformat()
                task['result'] = str(result)

        if self.tracker:
            self.tracker.log_activity(
                app_name='TaskExecutor',
                activity_type='task_completed',
                title=task_id,
                content=str(result)
            )

    def _log_task_error(self, task_id: str, error: str):
        """Log task error"""
        for task in self.task_history:
            if task['id'] == task_id:
                task['status'] = 'failed'
                task['error'] = error
                task['failed_at'] = datetime.now().isoformat()

        if self.tracker:
            self.tracker.log_activity(
                app_name='TaskExecutor',
                activity_type='task_failed',
                title=task_id,
                content=error
            )

    def get_task_history(self, limit: int = 20) -> list[Dict]:
        """Get task execution history"""
        return self.task_history[-limit:]

    def get_task_by_id(self, task_id: str) -> Optional[Dict]:
        """Get a specific task by ID"""
        for task in self.task_history:
            if task['id'] == task_id:
                return task
        return None
