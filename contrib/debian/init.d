#! /bin/sh
#

PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin
DAEMON=/usr/bin/freevo
NAME=freevo
DESC=freevo

test -x $DAEMON || exit 0

# Include freevo defaults if available
if [ -f /etc/freevo/boot_config ] ; then
	. /etc/freevo/boot_config
fi

set -e

[ "${NOMOUSE}" = "true" ] && {
    export SDL_NOMOUSE=true
}


case "$1" in
  start)
	echo -n "Starting $DESC: "
        $DAEMON start
	echo "$NAME."
	;;
  stop)
	echo -n "Stopping $DESC: "
        $DAEMON stop
	echo "$NAME."
	;;
  restart)
	echo -n "Restarting $DESC: "
        $DAEMON stop
	sleep 1
        $DAEMON start
	echo "$NAME."
	;;
  *)
	N=/etc/init.d/$NAME
	# echo "Usage: $N {start|stop|restart|reload|force-reload}" >&2
	echo "Usage: $N {start|stop|restart}" >&2
	exit 1
	;;
esac

exit 0
