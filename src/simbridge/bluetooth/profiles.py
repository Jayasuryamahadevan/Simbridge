"""Parse PipeWire/PulseAudio-compatible Bluetooth card profile listings."""

from __future__ import annotations

import re
from dataclasses import dataclass


_CARD_HEADER = re.compile(r"^Card #\d+\s*$")
_CARD_NAME = re.compile(r"^\s*Name:\s*(\S+)\s*$")
_ACTIVE_PROFILE = re.compile(r"^\s*Active Profile:\s*(.*?)\s*$")
_PROFILE_ENTRY = re.compile(r"^\s{2,}([A-Za-z0-9_.:-]+):\s*(.*?)\s*$")
_AVAILABILITY = re.compile(r"available:\s*(yes|no)", re.IGNORECASE)


@dataclass(frozen=True, slots=True)
class BluetoothProfile:
    name: str
    description: str
    available: bool | None

    @property
    def is_hfp_or_hsp(self) -> bool:
        value = f"{self.name} {self.description}".lower()
        return any(term in value for term in ("hfp", "hsp", "handsfree", "hands-free", "headset"))


@dataclass(frozen=True, slots=True)
class BluetoothAudioCard:
    name: str
    active_profile: str | None
    profiles: tuple[BluetoothProfile, ...]

    @property
    def voice_profiles(self) -> tuple[BluetoothProfile, ...]:
        return tuple(profile for profile in self.profiles if profile.is_hfp_or_hsp)


def parse_bluetooth_cards(output: str) -> tuple[BluetoothAudioCard, ...]:
    """Extract BlueZ cards and advertised voice profiles from card-list output."""
    blocks: list[list[str]] = []
    current: list[str] = []

    for line in output.splitlines():
        if _CARD_HEADER.match(line):
            if current:
                blocks.append(current)
            current = [line]
        elif current:
            current.append(line)
    if current:
        blocks.append(current)

    cards: list[BluetoothAudioCard] = []
    for lines in blocks:
        card_name: str | None = None
        active_profile: str | None = None
        profiles: list[BluetoothProfile] = []
        in_profiles = False
        profiles_indent = 0

        for line in lines:
            name_match = _CARD_NAME.match(line)
            if name_match:
                card_name = name_match.group(1)
                continue

            active_match = _ACTIVE_PROFILE.match(line)
            if active_match:
                active_profile = active_match.group(1) or None
                in_profiles = False
                continue

            if line.strip() == "Profiles:":
                in_profiles = True
                profiles_indent = len(line) - len(line.lstrip())
                continue

            if in_profiles:
                indent = len(line) - len(line.lstrip())
                if line.strip() and indent <= profiles_indent:
                    in_profiles = False
                    continue
                match = _PROFILE_ENTRY.match(line)
                if not match:
                    continue
                profile_name, description = match.groups()
                availability_match = _AVAILABILITY.search(description)
                availability = None
                if availability_match:
                    availability = availability_match.group(1).lower() == "yes"
                profiles.append(
                    BluetoothProfile(
                        name=profile_name,
                        description=description,
                        available=availability,
                    )
                )

        if card_name and (card_name.startswith("bluez_card.") or "bluez" in card_name):
            cards.append(
                BluetoothAudioCard(
                    name=card_name,
                    active_profile=active_profile,
                    profiles=tuple(profiles),
                )
            )

    return tuple(cards)


def format_bluetooth_profiles(output: str) -> str:
    cards = parse_bluetooth_cards(output)
    if not cards:
        return (
            "No Bluetooth audio cards are currently exposed by PipeWire.\n"
            "Pair and connect the phone, enable its Phone calls profile, then inspect again."
        )

    lines = ["Bluetooth audio profiles", "========================"]
    for card in cards:
        lines.extend(["", f"Card: {card.name}", f"Active profile: {card.active_profile or 'unknown'}"])
        if not card.profiles:
            lines.append("  No profiles were reported.")
            continue
        for profile in card.profiles:
            availability = (
                "available" if profile.available is True
                else "unavailable" if profile.available is False
                else "availability unknown"
            )
            voice_tag = " [HFP/HSP candidate]" if profile.is_hfp_or_hsp else ""
            active_tag = " [ACTIVE]" if profile.name == card.active_profile else ""
            lines.append(
                f"  {profile.name}: {profile.description} ({availability})"
                f"{voice_tag}{active_tag}"
            )

    if any(card.voice_profiles for card in cards):
        lines.extend([
            "",
            "Voice profile advertised: YES",
            "This indicates profile availability only; it does not prove live call audio works.",
        ])
    else:
        lines.extend([
            "",
            "Voice profile advertised: NO",
            "No HFP/HSP profile was found in the reported Bluetooth cards.",
        ])
    return "\n".join(lines)
