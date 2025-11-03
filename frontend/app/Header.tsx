import { Switch } from "@/components/ui/switch";
import { Mode } from "./types";

interface HeaderProps {
  mode: Mode;
  setMode: React.Dispatch<React.SetStateAction<Mode>>;
}

const Header: React.FC<HeaderProps> = ({ mode, setMode }: HeaderProps) => {
  const handleToggle = (checked: boolean) => {
    setMode(checked ? "Auto" : "Manual");
    console.log(checked ? "Auto" : "Manual");
  };
  return (
    <header className="sticky top-0 z-50 w-full border-b h-12 flex items-center justify-between px-4">
      {/* Left-justified */}
      <div className="text-lg font-semibold">Header</div>

      {/* Right-justified */}
      <div className="flex items-center space-x-2">
        <div className="text-app-info">Auto</div>
        <Switch checked={mode === "Auto"} onCheckedChange={handleToggle} />
      </div>
    </header>
  );
};
export default Header;
