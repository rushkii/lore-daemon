# SPDX-License-Identifier: GPL-2.0-only
#
# Copyright (C) 2022  Muhammad Rizki <kiizuha@gnuweeb.org>
#


# built-in/dev package imports
import asyncio
from typing import Any
from functools import wraps

# Discord imports
import discord
from discord import Interaction

# gnuweeb package import
from dscord import config
from logger import BotLogger


def lore_admin(func):
	@wraps(func)
	async def callback(*args: Any, **kwargs: Any) -> Any:
		i: "Interaction" = args[1]
		user_roles = [role.id for role in i.user.roles]

		if config.ADMIN_ROLE_ID not in user_roles:
			return await i.response.send_message(
				"Sorry, you don't have this permission\n"\
				"Tell the server admin to add you lore admin role.",
				ephemeral=True
			)
		if config.ADMIN_ROLE_ID in user_roles:
			return await func(*args, **kwargs)

	return callback


def wait_on_limit(func):
	@wraps(func)
	async def callback(*args: Any) -> Any:
		while True:
			try:
				return await func(*args)
			except discord.errors.RateLimited as e:
				# Calling logger attr from the GWClient() class
				logger = args[0].logger

				_flood_exceptions(e)
				logger.info("Woken up from flood wait...")
	return callback


async def _flood_exceptions(e: "discord.errors.RateLimited", logger: BotLogger):
	wait = e.retry_after
	logger.info(f"Sleeping for {wait} seconds due to Discord limit")
	await asyncio.sleep(wait)
