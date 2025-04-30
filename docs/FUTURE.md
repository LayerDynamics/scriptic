# Scriptic Implementation Plan

This document outlines a strategic approach to implementing and extending Scriptic for different application requirements.

## Core Implementation Overview

Scriptic has been implemented with the following design principles:

1. **Minimalism**: Single-file core with no external dependencies
2. **Extensibility**: Well-defined extension points via commands and subclassing
3. **Isolation**: Safe execution context with proper error handling
4. **Terminal-friendly**: Works well in standard terminal environments

## Implementation Phases

### Phase 1: Core REPL (Completed)

- [x] Basic REPL loop with input/eval/print cycle
- [x] Support for multiline input
- [x] Safe execution context
- [x] Signal handling (Ctrl+C, Ctrl+D)
- [x] Basic command registration
- [x] Context injection

### Phase 2: Extensions and Enhancements

- [x] Enhanced command system with decorators
- [x] Script loading
- [x] Execution timing
- [x] Command history
- [x] Custom styling options

### Phase 3: Future Improvements

- [ ] Auto-indentation for better code block handling
- [ ] Enhanced line editing (when readline is available)
- [ ] Remote REPL capabilities (via sockets)
- [ ] Logging and debugging hooks
- [ ] Session persistence

## Use Case Implementations

### 1. Application Debugging Console

For adding a debugging console to an existing application:

1. Create a global REPL instance with application context
2. Register debugging commands for common operations
3. Add activation trigger (e.g., hotkey, admin endpoint, etc.)

```python
# In your application's debug module
from scriptic import Scriptic

def create_debug_console(app):
    """Create a debug console for the application."""
    repl = Scriptic(context={
        "app": app,
        "models": app.models,
        "config": app.config,
        # More app objects as needed
    })
    
    # Register debugging commands
    repl.register_command("status", lambda _: app.print_status())
    repl.register_command("reload", lambda _: app.reload_config())
    repl.register_command("users", lambda _: print(app.list_users()))
    
    return repl

# Activation (e.g., in your main app)
def activate_debug_console():
    """Start the debug console when triggered."""
    console = create_debug_console(app)
    console.run()

# Hook to your activation mechanism
# Example: keyboard shortcut, admin command, etc.
```

### 2. Data Analysis Tool

For data science applications:

1. Pre-populate with common libraries and data
2. Add specialized visualization commands
3. Configure with domain-specific helpers

```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scriptic import Scriptic

class DataREPL(Scriptic):
    """Specialized REPL for data analysis."""
    
    def __init__(self, data_sources=None):
        # Initialize with data science context
        context = {
            "np": np,
            "pd": pd,
            "plt": plt,
            "data": data_sources or {},
        }
        super().__init__(context=context)
        
        # Register data commands
        self.register_command("load_csv", self._cmd_load_csv)
        self.register_command("plot", self._cmd_plot)
        self.register_command("describe", self._cmd_describe)
    
    def _cmd_load_csv(self, args):
        """Load a CSV file as a DataFrame."""
        path = args.strip()
        try:
            df = pd.read_csv(path)
            name = path.split("/")[-1].split(".")[0]
            self.context[name] = df
            print(f"Loaded as '{name}' DataFrame with {len(df)} rows")
        except Exception as e:
            print(f"Error loading CSV: {e}")
    
    def _cmd_plot(self, args):
        """Quick plot a variable."""
        try:
            eval(f"plt.figure(figsize=(10, 6)); {args}; plt.show()", self.context)
        except Exception as e:
            print(f"Plot error: {e}")
    
    def _cmd_describe(self, args):
        """Describe a DataFrame or Series."""
        try:
            result = eval(args, self.context)
            if hasattr(result, 'describe'):
                print(result.describe())
            else:
                print(f"Cannot describe object of type {type(result)}")
        except Exception as e:
            print(f"Error: {e}")
```

### 3. Plugin System

For applications with plugin capabilities:

1. Extend Scriptic to load plugins
2. Allow plugins to register their own commands
3. Manage plugin lifecycle and isolation

```python
import importlib.util
import os
from scriptic import Scriptic

class PluginScriptic(Scriptic):
    """REPL with plugin support."""
    
    def __init__(self, plugin_dir="plugins"):
        super().__init__()
        self.plugin_dir = plugin_dir
        self.plugins = {}
        
        # Register plugin commands
        self.register_command("load_plugin", self._cmd_load_plugin)
        self.register_command("list_plugins", self._cmd_list_plugins)
        self.register_command("reload_plugin", self._cmd_reload_plugin)
        
        # Auto-load plugins if directory exists
        if os.path.isdir(plugin_dir):
            self._load_plugins()
    
    def _load_plugins(self):
        """Load all plugins from the plugin directory."""
        for filename in os.listdir(self.plugin_dir):
            if filename.endswith(".py"):
                self._load_plugin(filename[:-3])
    
    def _load_plugin(self, plugin_name):
        """Load a specific plugin by name."""
        try:
            path = os.path.join(self.plugin_dir, f"{plugin_name}.py")
            spec = importlib.util.spec_from_file_location(plugin_name, path)
            plugin = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(plugin)
            
            # Store the plugin
            self.plugins[plugin_name] = plugin
            
            # Register plugin commands if available
            if hasattr(plugin, "register_commands"):
                plugin.register_commands(self)
                
            print(f"Loaded plugin: {plugin_name}")
            return True
        except Exception as e:
            print(f"Error loading plugin {plugin_name}: {e}")
            return False
    
    def _cmd_load_plugin(self, args):
        """Command to load a plugin."""
        plugin_name = args.strip()
        if not plugin_name:
            print("Usage: %load_plugin plugin_name")
            return
        self._load_plugin(plugin_name)
    
    def _cmd_list_plugins(self, args):
        """List all loaded plugins."""
        if not self.plugins:
            print("No plugins loaded.")
            return
            
        print("Loaded plugins:")
        for name, plugin in self.plugins.items():
            desc = getattr(plugin, "__doc__", "No description")
            print(f"  {name}: {desc}")
    
    def _cmd_reload_plugin(self, args):
        """Reload a plugin."""
        plugin_name = args.strip()
        if not plugin_name:
            print("Usage: %reload_plugin plugin_name")
            return
            
        if plugin_name in self.plugins:
            del self.plugins[plugin_name]
            self._load_plugin(plugin_name)
        else:
            print(f"Plugin not loaded: {plugin_name}")
```

### 4. Web App Integration

To add a REPL to a Flask or Django web application:

```python
# In a Flask app
from flask import Flask
from scriptic import Scriptic
import threading

app = Flask(__name__)

def start_repl():
    """Start a REPL with access to the Flask app."""
    repl = Scriptic(context={
        "app": app,
        "db": db,  # Your database connection
        "config": app.config,
    })
    
    @repl.command()
    def routes(args):
        """List all registered routes."""
        for rule in app.url_map.iter_rules():
            print(f"{rule.endpoint}: {rule}")
    
    @repl.command()
    def test_route(args):
        """Test a route with a mock request."""
        with app.test_client() as client:
            response = client.get(args.strip())
            print(f"Status: {response.status_code}")
            print(f"Response: {response.data.decode()[:200]}...")
    
    repl.run()

# Start the REPL in a separate thread when the app starts
@app.before_first_request
def initialize():
    repl_thread = threading.Thread(target=start_repl)
    repl_thread.daemon = True  # Thread will exit when main thread exits
    repl_thread.start()
```

## Deployment Considerations

1. **Security**: Don't expose the REPL in production unless behind strong authentication
2. **Resources**: Monitor memory usage as the REPL context can grow over time
3. **Isolation**: Consider running the REPL in a separate process for critical applications
4. **Documentation**: Document available commands and objects for users

## Testing Strategy

1. **Unit Testing**: Core functionality using mocked inputs
2. **Integration Testing**: Full REPL with actual input scenarios
3. **Extension Testing**: Test custom commands and hooks
4. **Edge Cases**: 
   - Handling large inputs
   - Memory management
   - Signal interruption
   - Syntax errors
   - Runtime exceptions

## Conclusion

This implementation plan provides a structured approach to integrating and extending Scriptic for various application needs. The modular design allows for customization while maintaining a minimal core that can be easily understood and maintained.

By following these patterns, you can create specialized REPL environments tailored to your specific application domains while leveraging the robust foundation of the Scriptic core.