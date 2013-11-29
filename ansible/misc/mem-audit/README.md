Generate a report of the memory usage on ansible-managed hosts. This
can be thought of as a network-wide ps(1). The report can be generated
by running the make(1) command.

That they are ansible-managed is accidental -- but the Makefile uses
the inventory to get the list of hosts. It does not use ansible
directly (though it could) because parsing ansible's output is
unreliable. This is because it expects that it might be run in a
multi-threaded way and doesn't appear to take measures to properly
serialise its output so that it can be processed by another
program. That's not the UNIX Way. But I digress.

The scripts run ps and look in /proc/meminfo. They sum the resident
size of the programs running, and compare that the the total
memory. Similar comparisons are done for kernel I/O buffers and cache,
as well as swap space usage. A report is generated to standard output.

Sometimes a server appears to have overcommitted memory, sometimes by
a significant margin 3-4x. This is almost always postgresql which
makes heavy use of CoW with its child processes sharing much of the
parent's address space. Inspecting the column with buffers shows that
actually the apparent memory usage is unrealistically high, and there
is still (or should be) plenty of RAM for I/O buffering which is
critical to database performance.
