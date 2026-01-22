import { MainNav } from "./MainNav";
import { MobileNav } from "./MobileNav";

export const Header = () => {
  return (
    <header className="sticky top-0 z-50 w-full border-b bg-white text-neutral-900">
      <div className="flex h-14 mx-2 items-center">
        <MainNav />
        <MobileNav />
      </div>
    </header>
  );
};
