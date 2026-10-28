# SPDX-License-Identifier: Apache-2.0
board_runner_args(jlink "--device=nrf5340_xxaa_app" "--speed=1000")
include(${ZEPHYR_BASE}/boards/common/jlink.board.cmake)
