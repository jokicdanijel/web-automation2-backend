/**
 * Automation Script Handler
 * Orchestrates multiple automation actions in sequence
 * Supports workflows with error handling and state tracking
 */

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const { workflow } = req.body;

    if (!workflow || !Array.isArray(workflow.actions)) {
      return res.status(400).json({
        error: 'Invalid workflow format. Expected: { workflow: { actions: [...], options?: {...} } }'
      });
    }

    const results = [];
    const context = {
      timestamp: new Date().toISOString(),
      executedActions: 0,
      failedActions: 0
    };

    // Execute workflow actions sequentially
    for (let i = 0; i < workflow.actions.length; i++) {
      const action = workflow.actions[i];
      
      try {
        const actionResult = await executeAction(action, context, results);
        
        results.push({
          actionIndex: i,
          action: action.type,
          status: 'success',
          result: actionResult,
          timestamp: new Date().toISOString()
        });

        context.executedActions++;

        // Optional: wait between actions if specified
        if (action.waitAfter) {
          await new Promise(resolve => setTimeout(resolve, action.waitAfter));
        }

      } catch (error) {
        context.failedActions++;
        
        results.push({
          actionIndex: i,
          action: action.type,
          status: 'error',
          error: error.message,
          timestamp: new Date().toISOString()
        });

        // Stop workflow on error if stopOnError is true
        if (workflow.stopOnError !== false) {
          throw error;
        }
      }
    }

    return res.status(200).json({
      success: true,
      summary: {
        totalActions: workflow.actions.length,
        executedActions: context.executedActions,
        failedActions: context.failedActions,
        duration: `${Date.now() - new Date(context.timestamp).getTime()}ms`
      },
      results,
      context
    });

  } catch (error) {
    return res.status(500).json({
      error: 'Workflow execution failed',
      details: error.message
    });
  }
}

/**
 * Execute individual action
 * Supports: navigate, click, type, extract, wait, scroll, screenshot
 */
async function executeAction(action, context, previousResults) {
  switch (action.type) {
    case 'navigate':
      return {
        url: action.url,
        message: `Navigated to ${action.url}`
      };

    case 'click':
      return {
        selector: action.selector,
        message: `Clicked on ${action.selector}`
      };

    case 'type':
      return {
        selector: action.selector,
        text: action.text,
        message: `Typed text into ${action.selector}`
      };

    case 'extract':
      return {
        selector: action.selector,
        message: `Extracted data from ${action.selector}`
      };

    case 'wait':
      const waitTime = action.duration || 1000;
      await new Promise(resolve => setTimeout(resolve, waitTime));
      return {
        duration: waitTime,
        message: `Waited ${waitTime}ms`
      };

    case 'scroll':
      return {
        direction: action.direction || 'down',
        distance: action.distance || 500,
        message: `Scrolled ${action.direction || 'down'} by ${action.distance || 500}px`
      };

    case 'screenshot':
      return {
        name: action.name,
        message: `Screenshot taken: ${action.name}`
      };

    case 'condition':
      // Execute based on previous results
      if (action.checks) {
        for (const check of action.checks) {
          if (previousResults.length > check.resultIndex) {
            const prevResult = previousResults[check.resultIndex];
            if (check.condition === 'success' && prevResult.status === 'success') {
              return { condition: true, message: 'Condition met' };
            }
          }
        }
      }
      return { condition: false, message: 'Condition not met' };

    default:
      throw new Error(`Unknown action type: ${action.type}`);
  }
}
