#!/bin/bash
# ----------------------------------------------------------------------
# mikes handy rotating-filesystem-snapshot utility
# ----------------------------------------------------------------------
# this needs to be a lot more general, but the basic idea is it makes
# rotating backup-snapshots of /home whenever called
# ----------------------------------------------------------------------

unset PATH	# suggestion from H. Milz: avoid accidental use of $PATH

# ------------- system commands used by this script --------------------
ID=/usr/bin/id;
ECHO=/bin/echo;

MOUNT=/bin/mount;
UMOUNT=/bin/umount;
RM=/bin/rm;
MV=/bin/mv;
CP=/bin/cp;
TOUCH=/bin/touch;
LOCKFILE=/usr/bin/lockfile;
NICE=/usr/bin/nice
RSYNC=/usr/bin/rsync;


# ------------- file locations -----------------------------------------

MOUNT_DEVICE=/dev/sdb1;
SNAPSHOT_RW=/mnt/backup;
EXCLUDES=/etc/backup_exclude;
HOST=eu0;
LOCK=/tmp/lock.snapshot;
BACKUP_SCRIPTDIR=/etc/backupscripts

# ------------- the script itself --------------------------------------

# make sure we're running as root
if (( `$ID -u` != 0 )); then { $ECHO "Sorry, must be root.  Exiting..."; exit; } fi

# attempt to get a lock
$LOCKFILE -r0 $LOCK;
if (( $? )); then
{
	$ECHO "snapshot: could not acquire lock exiting";
	exit;
}
fi;


# rotating snapshots of /home (fixme: this should be more general)

# step 1: delete the oldest snapshot, if it exists:
if [ -d $SNAPSHOT_RW/$HOST/daily.3 ] ; then			\
$RM -rf $SNAPSHOT_RW/$HOST/daily.3 ;				\
fi ;

# step 2: shift the middle snapshots(s) back by one, if they exist
if [ -d $SNAPSHOT_RW/$HOST/daily.2 ] ; then			\
$MV $SNAPSHOT_RW/$HOST/daily.2 $SNAPSHOT_RW/$HOST/daily.3 ;	\
fi;
if [ -d $SNAPSHOT_RW/$HOST/daily.1 ] ; then			\
$MV $SNAPSHOT_RW/$HOST/daily.1 $SNAPSHOT_RW/$HOST/daily.2 ;	\
fi;

# step 3: make a hard-link-only (except for dirs) copy of the latest snapshot,
# if that exists
if [ -d $SNAPSHOT_RW/$HOST/daily.0 ] ; then			\
$NICE -n 19 $CP -al $SNAPSHOT_RW/$HOST/daily.0 $SNAPSHOT_RW/$HOST/daily.1 ;	\
fi;

# step 3.5: run /etc/backupscripts/00mysql, 01syncfoo, etc
#
for scr in ${BACKUP_SCRIPTDIR}/[0-9][0-9]*; do
	if [ -x ${scr} ]; then
		${scr}
	fi
done

# step 4: rsync from the system into the latest snapshot (notice that
# rsync behaves like cp --remove-destination by default, so the destination
# is unlinked first.  If it were not so, this would copy over the other
# snapshot(s) too!
$NICE -n 19 $RSYNC								\
	-aR --delete --delete-excluded				\
	--exclude-from="$EXCLUDES"				\
	/home/ $SNAPSHOT_RW/$HOST/daily.0 ;

# step 5: update the mtime of daily.0 to reflect the snapshot time
$TOUCH $SNAPSHOT_RW/$HOST/daily.0 ;

# and thats it for home.

# release lock
$RM $LOCK

