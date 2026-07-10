from github_tools.github_api import (
    get_repository,
    get_repository_content
)

repo = get_repository("octocat/Hello-World")
print(repo)

content = get_repository_content(repo)


print(content)
