# Simple sudo role

This role sets up a simple sudoers file. Each user has full sudo access, and a
global setting determines whether NOPASSWD is set or not.

## Variables

 * sudo_users - A list of users who have sudo access. Use '%foo' to specify
   that users in a given group have sudo access.
   * default: root, users in group wheel
 * sudo_nopasswd - if set, NOPASSWD is added to all sudoers entries. Use this
   when users don't have passwords set.
   * default: true
