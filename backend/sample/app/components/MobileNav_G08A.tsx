"use client"
import { AlignJustify, House } from "lucide-react"
import Link from "next/link"
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetTrigger } from "@/components/ui/sheet"

const MobileNav = () => {
  return (
    <div data-testid="mobile-nav" className="md:hidden">
      <Sheet>
        <SheetTrigger>
          <AlignJustify />
        </SheetTrigger>
        <SheetContent side="left">
          <SheetHeader>
            <SheetTitle>ホテル東京</SheetTitle>
            <Link href="/">
              <House size={20} />
            </Link>
            <nav>
              <Link href="/rooms">
                客室
              </Link>
              <Link href="/dining">
                ダイニング
              </Link>
            </nav>
          </SheetHeader>
        </SheetContent>
      </Sheet>
    </div>
  );
};

export default MobileNav;