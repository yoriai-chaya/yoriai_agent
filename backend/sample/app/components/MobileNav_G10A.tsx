"use client"
import { AlignJustify, House } from "lucide-react"
import Link from "next/link"
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetTrigger } from "@/components/ui/sheet"

const MobileNav = () => {
  return (
    <div data-testid="mobile-nav" className="md:hidden w-full">
      <div className="grid grid-cols-3 items-center h-14 px-4 gap-4">
        <div className="flex items-center">
          <Sheet>
            <SheetTrigger>
              <AlignJustify />
            </SheetTrigger>
            <SheetContent side="left">
              <SheetHeader>
                <SheetTitle>ホテル東京</SheetTitle>
                <Link href="/" data-testid="mobile-navbar-link-home">
                  <House size={20} />
                </Link>
                <nav>
                  <Link href="/rooms" data-testid="mobile-navbar-link-rooms">
                    客室
                  </Link>
                  <Link href="/dining" data-testid="mobile-navbar-link-dining">
                    ダイニング
                  </Link>
                </nav>
              </SheetHeader>
            </SheetContent>
          </Sheet>
        </div>
        <div className="text-center font-medium text-gray-700 text-lg" data-testid="mobile-navbar-title">
          ホテル東京
        </div>
        <div className="text-right">
          (Mode)
        </div>
      </div>
    </div>
  );
};

export default MobileNav;