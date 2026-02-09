using System.Collections.Generic;
using Robust.Client.UserInterface;

namespace Content.Client.Stylesheets
{
    public sealed class DummyStylesheetManager : IStylesheetManager
    {
        public Stylesheet SheetNano { get; } = new Stylesheet(new List<StyleRule>());
        public Stylesheet SheetSpace { get; } = new Stylesheet(new List<StyleRule>());

        public DummyStylesheetManager()
        {

        }

        public void Initialize()
        {

        }
    }
}
