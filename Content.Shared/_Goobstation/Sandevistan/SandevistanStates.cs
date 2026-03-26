using Robust.Shared.Serialization;

namespace Content.Goobstation.Shared.Sandevistan;

[Serializable, NetSerializable]
public enum SandevistanState : byte
{
    Normal = 0,
    Warning = 1,
    Shaking = 2,
    Stamina = 3,
    Damage = 4,
    Knockdown = 5,
    Disable = 6,
    Death = 7, // Not used but I'll leave this for yaml warriors
}
