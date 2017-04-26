# mrm-tests

Tests for [replication-manager](https://github.com/tanji/replication-manager)
and [MaxScale](https://github.com/mariadb-corporation/MaxScale).

Running tests requires:

 - Python 3
 - transitions (pip3 install transitions)

Edit the following files to do the following actions:

- `start.sh`: Start a node, either 0 or 1 is given as parameter for either first or second node
- `stop.sh`: Stop a node, same parameters as start
- `check.sh`: Print cluster status to stdout, intended to be used with maxadmin

## Test syntax

The tests consist of two a node setup with one master and one slave. Each line
in a .test file is considered a state of the cluster. Here's an example:

```
MS
MX
MS
```

This starts with the first server as Master (M) and the second server as Slave
(S). Then the second server goes down (X) and is restarted again.
