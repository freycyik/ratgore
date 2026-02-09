using Content.Shared.GameTicking.Prototypes;
using Robust.Shared.Random;
using System.Linq;
using Content.Shared._OS;
using Robust.Shared.Utility;
using Robust.Shared.Serialization.Markdown.Mapping;

namespace Content.Server.GameTicking;

public sealed partial class GameTicker
{
    [ViewVariables]
    public LobbyBackgroundPrototype? LobbyBackground { get; private set; }

    [ViewVariables]
    private List<LobbyBackgroundPrototype> _lobbyBackgrounds = new();

    private static readonly string[] WhitelistedBackgroundExtensions = { "png", "jpg", "jpeg", "webp", "rsi" };

    private void InitializeLobbyBackground()
    {
        _lobbyBackgrounds.Clear();

        // 1. Загружаем стандартные статичные фоны
        foreach (var prototype in _prototypeManager.EnumeratePrototypes<LobbyBackgroundPrototype>())
        {
            if (!WhitelistedBackgroundExtensions.Contains(prototype.Background.Extension))
            {
                _sawmill.Warning($"Lobby background '{prototype.ID}' has an invalid extension '{prototype.Background.Extension}' and will be ignored.");
                continue;
            }

            _lobbyBackgrounds.Add(prototype);
        }

        foreach (var aniProto in _prototypeManager.EnumeratePrototypes<AnimatedLobbyScreenPrototype>())
        {
            var name = "Тут должно быть название фона";
            var artist = "Тут должен быть автор фона";

            if (_prototypeManager.TryGetMapping(typeof(AnimatedLobbyScreenPrototype), aniProto.ID, out var mapping))
            {
                if (mapping.TryGet("name", out var nameNode))
                    name = nameNode.ToString();
                
                if (mapping.TryGet("artist", out var artistNode))
                    artist = artistNode.ToString();
            }

            _lobbyBackgrounds.Add(new LobbyBackgroundPrototype
            {
                Background = new ResPath(aniProto.Path),
                Name = name,
                Artist = artist
            });
            
            _sawmill.Debug($"Animated background loaded: {aniProto.ID} ({name} by {artist})");
        }

        if (_lobbyBackgrounds.Count == 0)
            _sawmill.Error("Lobby background pool is empty!");

        RandomizeLobbyBackground();
    }

    private void RandomizeLobbyBackground()
    {
        LobbyBackground = _lobbyBackgrounds.Count > 0 ? _robustRandom.Pick(_lobbyBackgrounds) : null;
        
        if (LobbyBackground != null)
            _sawmill.Info($"Selected lobby background: {LobbyBackground.Background} (Name: {LobbyBackground.Name})");
    }
}