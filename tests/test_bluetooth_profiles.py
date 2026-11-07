from simbridge.bluetooth.profiles import (
    format_bluetooth_profiles,
    parse_bluetooth_cards,
)


SAMPLE_CARDS = """
Card #41
    Name: alsa_card.pci-0000_00_1f.3
    Profiles:
        output:analog-stereo: Analog Stereo Output (priority 6500, available: yes)
    Active Profile: output:analog-stereo

Card #52
    Name: bluez_card.11_22_33_44_55_66
    Profiles:
        a2dp-sink: High Fidelity Playback (A2DP Sink) (priority 40, available: yes)
        headset-head-unit: Headset Head Unit (HSP/HFP) (priority 30, available: yes)
        headset-head-unit-msbc: Headset Head Unit (HSP/HFP, codec mSBC) (priority 35, available: yes)
        off: Off (priority 0, available: yes)
    Active Profile: a2dp-sink
"""


def test_parser_only_returns_bluetooth_cards() -> None:
    cards = parse_bluetooth_cards(SAMPLE_CARDS)
    assert len(cards) == 1
    assert cards[0].name == "bluez_card.11_22_33_44_55_66"


def test_parser_identifies_voice_profiles_and_active_profile() -> None:
    card = parse_bluetooth_cards(SAMPLE_CARDS)[0]
    assert card.active_profile == "a2dp-sink"
    assert {profile.name for profile in card.voice_profiles} == {
        "headset-head-unit",
        "headset-head-unit-msbc",
    }
    assert all(profile.available is True for profile in card.voice_profiles)


def test_profile_report_does_not_claim_call_audio_is_verified() -> None:
    report = format_bluetooth_profiles(SAMPLE_CARDS)
    assert "Voice profile advertised: YES" in report
    assert "does not prove live call audio works" in report


def test_missing_bluetooth_card_is_reported() -> None:
    report = format_bluetooth_profiles("Card #1\n    Name: alsa_card.internal\n")
    assert "No Bluetooth audio cards" in report
