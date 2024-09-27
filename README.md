# Djangoly: Write Cleaner, Faster, Scalable Django Code

Djangoly is a VS Code extension built for Django developers (surprise, surprise). It uses static analysis to ensure your project aligns with Django best practices and conventions. You can install the extension via the [VS Code Marketplace](https://marketplace.visualstudio.com/items?itemName=Alchemized.djangoly) or by searching for `djangoly` in your IDE's extension tab.

## Requirements

1. VS Code 1.64.0 or greater
2. Python 3.9 or greater
3. node >= 18.17.0

## Features ✨

- **Django-Specific Linting**: Automatically check your Django code against best practices and common pitfalls, including:

  - **Complex View Detection**: Flags Django views with high complexity and suggests that they be refactored to follow the **Fat Model, Thin View** or **Services** design patterns. This rule reduces view complexity and promotes maintainability and scalability.
  - **ForeignKey Validation**: Ensures all `ForeignKey` fields have a `related_name` and `on_delete` argument specified to avoid common pitfalls in query relationships and data management.
  - **Raw SQL Query Detection**: Flags direct usage of raw SQL queries, including `raw()` and `connection.cursor()`. These can bypass Django ORM protections and introduce security vulnerabilities. Djangoly suggests safer alternatives using Django's ORM.
  - **CharField and TextField Nullability**: Ensures `CharField` and `TextField` fields are not incorrectly marked as `null=True`, which can lead to inconsistencies in data integrity.
  - **Missing Exception Handling Detection**: Flags Django functional views and methods in class-based views that lack exception handling. This feature helps you ensure that error handling is properly implemented, improving the robustness and stability of your Django application.
- **Security Checks**: Includes several security checks to help ensure your Django project follows best practices for security:

  - **DEBUG Setting**: Checks if `DEBUG` is set to `True`. This setting should be `False` in production environments.
  - **SECRET_KEY Protection**: Verifies that the `SECRET_KEY` is not hardcoded in your settings file.
  - **ALLOWED_HOSTS Configuration**: Checks the `ALLOWED_HOSTS` setting for potential security issues.
  - **COOKIE Settings**: Ensures the `CSRF_COOKIE_SECURE` and `SESSION_COOKIE_SECURE` settings are set to `True` for production environments.
- **Test Suite Conventions**: Notify developers to add or update test files when changes are detected in Django views or models.
- **Redundant Comment Detection**: Flags comments that do not contribute additional information or context to the code.

## Djangoly Convention and Security Rules 📏🔒

Djangoly implements a comprehensive set of rules to help you write cleaner, safer, and more efficient Django code. These rules cover various aspects of Django development, including:

* **Security (SEC)**: Checks for proper security settings and practices.

  * Example: Ensuring DEBUG is set to False in production.
* **Code Quality (CDQ)**: Enforces coding standards and best practices.

  * Example: Detecting overly complex views that should be refactored.
* **Style (STY)**: Ensures consistent coding style across your project.

  * Example: Enforcing naming conventions for variables and functions.
* **Configuration (CFG)**: Verifies correct Django configuration settings.

  * Example: Checking for proper ALLOWED\_HOSTS configuration.

Each rule is designed to catch common pitfalls, enforce best practices, and improve the overall quality and security of your Django projects.

For a complete list of all rules, including detailed descriptions and examples, please refer to our [Convention Rules Documentation](https://github.com/software-trizzey/djangoly-docs/blob/main/docs/CONVENTION_RULES.md).

By following these rules, you can ensure that your Django code is not only functional but also secure, efficient, and maintainable.

## Quick Start 🏃‍♂️💨

1. **Get an API Key**: If you don't already have an API key, you can signup for one via this [form](https://forms.gle/gEEZdfhWpQyQh2qVA).
2. **Install the Extension**: [VS Code Marketplace](https://marketplace.visualstudio.com/items?itemName=Alchemized.djangoly)
3. **Set Up Your Django Project**: If you haven't already, set up a Django project in your workspace.
4. **Configure Django Settings**: Open the extension settings in VS Code and configure your Django-specific settings.
5. **Start Coding**: Begin developing your Django project. The extension will automatically start analyzing your code.
6. **Review Suggestions**: Check the Problems panel in VS Code for Django best practice suggestions and quick fixes.

**Note**: To modify the extension rules, access these settings by going to `Preferences → Settings → Extensions → Djangoly`.

## How Djangoly Improves Your Code 🧑‍🏫

### 1. Missing Exception Handling Detection

![Djangoly exception handler demo](https://raw.githubusercontent.com/software-trizzey/images/main/assets/images/djangoly-exception-handler-demo.gif)

Djangoly ensures that your Django views and methods have proper error handling. It flags functions that lack try-except blocks and can create exception handlers based on your preferences and the function's context.

### 2. Security Settings Check

Before (in settings.py):

```python
DEBUG = True
SECRET_KEY = 'my_secret_key'
ALLOWED_HOSTS = ['*']
```

After (with Djangoly warnings):

```python
DEBUG = False  # Djangoly: Ensure DEBUG is False in production
SECRET_KEY = os.environ.get('SECRET_KEY')  # Djangoly: Use environment variables for sensitive data
ALLOWED_HOSTS = ['example.com', 'www.example.com']  # Djangoly: Specify allowed hosts explicitly
```

Djangoly identifies potential security risks in your Django settings and suggests safer alternatives.

### 2. Test Suite Conventions

![Djangoly untested code demo](https://raw.githubusercontent.com/software-trizzey/images/main/assets/images/flag-untested-api-code.gif)
Djangoly reminds you to create and update test files when you modify your Django views or models.

## Known Issues & Limitations 🐞

- **False Positives**: As an MVP undergoing rapid development, Djangoly may generate inaccurate diagnostics and recommendations. If you encounter any issues, please report them to [support@djangoly.com](mailto:support@djangoly.com).

## Join Our Community on Discord 💬

Have questions or run into issues? Join our [Discord server](https://discord.gg/U8Mq8Vx9q9) to connect with the development team and other users. You'll get faster responses to your questions, feedback, and issues, and you'll be able to discuss new features with the community.

# Extension Development

## Getting Started

1. Use this [template to create your repo](https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-repository-from-a-template).
2. Check-out your repo locally on your development machine.
3. Create and activate a python virtual environment for this project in a terminal. Be sure to use the minimum version of python for your tool. This template was written to work with python 3.8 or greater.
4. Install `nox` in the activated environment: `python -m pip install nox`.
5. Add your favorite tool to `requirements.in`
6. Run `nox --session setup`.
7. **Optional** Install test dependencies `python -m pip install -r src/test/python_tests/requirements.txt`. You will have to install these to run tests from the Test Explorer.

## Logging and Logs

The template creates a logging Output channel that can be found under `Output` > `mytool` panel. You can control the log level running the `Developer: Set Log Level...` command from the Command Palette, and selecting your extension from the list. It should be listed using the display name for your tool. You can also set the global log level, and that will apply to all extensions and the editor.

If you need logs that involve messages between the Language Client and Language Server, you can set `"mytool.server.trace": "verbose"`, to get the messaging logs. These logs are also available `Output` > `mytool` panel.

## Adding new Settings or Commands

You can add new settings by adding details for the settings in `package.json` file. To pass this configuration to your python tool server (i.e, `lsp_server.py`) update the `settings.ts` as need. There are examples of different types of settings in that file that you can base your new settings on.

You can follow how `restart` command is implemented in `package.json` and `extension.ts` for how to add commands. You can also contribute commands from Python via the Language Server Protocol.

## Testing

See `src/test/python_tests/test_server.py` for starting point. See, other referred projects here for testing various aspects of running the tool over LSP.

If you have installed the test requirements you should be able to see the tests in the test explorer.

You can also run all tests using `nox --session tests` command.

## Linting

Run `nox --session lint` to run linting on both Python and TypeScript code. Please update the nox file if you want to use a different linter and formatter.

## Packaging and Publishing

1. Update various fields in `package.json`. At minimum, check the following fields and update them accordingly. See [extension manifest reference](https://code.visualstudio.com/api/references/extension-manifest) to add more fields:
   - `"publisher"`: Update this to your publisher id from [https://marketplace.visualstudio.com/](https://marketplace.visualstudio.com/).
   - `"version"`: See [https://semver.org/](https://semver.org/) for details of requirements and limitations for this field.
   - `"license"`: Update license as per your project. Defaults to `MIT`.
   - `"keywords"`: Update keywords for your project, these will be used when searching in the VS Code marketplace.
   - `"categories"`: Update categories for your project, makes it easier to filter in the VS Code marketplace.
   - `"homepage"`, `"repository"`, and `"bugs"` : Update URLs for these fields to point to your project.
   - **Optional** Add `"icon"` field with relative path to a image file to use as icon for this project.
2. Make sure to check the following markdown files:
   - **REQUIRED** First time only: `CODE_OF_CONDUCT.md`, `LICENSE`, `SUPPORT.md`
   - Every Release: `CHANGELOG.md`
3. Build package using `nox --session build_package`.
4. Take the generated `.vsix` file and upload it to your extension management page [https://marketplace.visualstudio.com/manage](https://marketplace.visualstudio.com/manage).

To do this from the command line see here [https://code.visualstudio.com/api/working-with-extensions/publishing-extension](https://code.visualstudio.com/api/working-with-extensions/publishing-extension)
