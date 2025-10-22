import MainNav from "./MainNav";
import MobileNav from "./MobileNav";
const Header = () => {
  return (
    <header className="sticky top-0 w-full border-b z-50 text-gray-700 bg-white dark:text-gray-100 dark:bg-ctm-navy-800">
      <div className="h-14 flex items-center mx-2">
        {/* Desktop */}
        <MainNav />
        {/* Mobile */}
        <MobileNav />
      </div>
    </header>
  );
};
export default Header;
