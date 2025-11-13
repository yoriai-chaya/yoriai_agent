import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "@/components/ui/sheet";
import { AlignJustify } from "lucide-react";
import { House } from "lucide-react";
import Link from "next/link";
import { ModeToggle } from "./ModeToggle";

const MobileNav = () => {
  return (
    <div className="md:hidden w-full">
      <div className="grid grid-cols-3 items-center h-14 px-4">
        {/* A列 */}
        <div className="flex items-center">
          <Sheet>
            <SheetTrigger>
              <AlignJustify />
            </SheetTrigger>
            <SheetContent side="left">
              <SheetHeader>
                <SheetTitle>ホテル東京</SheetTitle>
                <nav className="flex flex-col items-start gap-3">
                  <Link href="/">
                    <House size={20} />
                  </Link>
                  <Link
                    href="/rooms"
                    className="text-ctm-blue-500 dark:text-ctm-yellow-200 hover:underline"
                  >
                    客室
                  </Link>
                  <Link
                    href="/dining"
                    className="text-ctm-blue-500 dark:text-ctm-yellow-200 hover:underline"
                  >
                    ダイニング
                  </Link>
                </nav>
              </SheetHeader>
            </SheetContent>
          </Sheet>
        </div>
        {/* B列 */}
        <div className="text-center text-lg font-medium text-gray-700 dark:text-gray-100">
          <div>ホテル東京</div>
        </div>
        {/* C列 */}
        <div className="flex justify-end items-center">
          <ModeToggle />
        </div>
      </div>
    </div>
  );
};
export default MobileNav;
