import { Switch } from "@/components/ui/switch";
import { Mode } from "./types";
import AutoBlock from "./AutoBlock";
import { Action, FileInfo } from "./types";

interface HeaderProps {
  mode: Mode;
  setMode: React.Dispatch<React.SetStateAction<Mode>>;
  dispatch: React.Dispatch<Action>;
  setFileInfo: React.Dispatch<React.SetStateAction<FileInfo[]>>;
}

const Header: React.FC<HeaderProps> = ({
  mode,
  setMode,
  dispatch,
  setFileInfo,
}: HeaderProps) => {
  const handleToggle = (checked: boolean) => {
    setMode(checked ? "Auto" : "Manual");
    console.log(checked ? "Auto" : "Manual");
  };
  return (
    <header className="sticky top-0 z-50 w-full border-b h-18 flex items-center justify-between px-4">
      {/* Left-justified */}
      <div className="text-lg font-semibold">Header</div>

      {/* Right-justified */}
      <div className="flex items-center">
        <AutoBlock dispatch={dispatch} setFileInfo={setFileInfo} />
        <div className="flex items-center space-x-2">
          <div className="text-app-info">Auto</div>
          <Switch checked={mode === "Auto"} onCheckedChange={handleToggle} />
        </div>
      </div>
    </header>
  );
};
export default Header;
