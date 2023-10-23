###  Thoughts about dealing with user UID/GID issues in Dockerfile or entrypoint

- The UID exists as a user
- 
- The UID does not exist as a user

```shell

id -un  UID # prints the user name for that user UID
id -gn  UID # prints the user primary group name for that UID
id -Gn  UID # prints all user groups for the user UID.


if id -un 1234; then
  # We have a user with that UID
else
  # We don't have a user with that UID

```