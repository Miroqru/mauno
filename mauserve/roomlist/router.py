"""Работа со списком комнат."""

from fastapi import APIRouter, HTTPException

from mauserve.models import UserModel

router = APIRouter(prefix="/leaderboard", tags=["rating"])
