# Apache mcumgr host tool

`linux-amd64/mcumgr` is a statically linked Linux x86_64 build of
https://github.com/apache/mynewt-mcumgr-cli at commit
5c56bd24066c780aad5836429bfa2ecc4f9a944c, built with Go 1.27.3 and CGO_ENABLED=0.
The upstream binary version string is `0.0.0-dev`; use the pinned source commit
and build-info.txt for provenance. LICENSE and dependency notices are included.

To build for another host with Go installed:

```
CGO_ENABLED=0 go install github.com/apache/mynewt-mcumgr-cli/mcumgr@5c56bd24066c780aad5836429bfa2ecc4f9a944c
```

Pass that executable with `usb_update.py --mcumgr /path/to/mcumgr` if it is not
on PATH. Source: Apache-2.0; transitive dependency notices under licenses/.
The wrapper only invokes image upload and reset commands.

The executable is ignored by Git. On Linux x86_64, build it with
`python3 firmware/tools/install_mcumgr.py` from the project root. This downloads
a checksum-verified Go toolchain into the ignored build directory and builds
only the pinned mcumgr source. No shell profile or system package is changed.
