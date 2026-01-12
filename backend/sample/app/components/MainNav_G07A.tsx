"use client"
import { SendHorizontal } from "lucide-react";
import Link from "next/link";
import { Button } from "@/components/ui/button";

const MainNav = () => {
  const handleSearch = () => {
    console.log('Button pressed');
  };

  return (
    <div data-testid="main-nav" className="hidden md:flex w-full">
      <nav className="grid grid-cols-3 w-full items-center gap-4">
        <div className="flex items-center gap-4">
          <Link href="/rooms">客室</Link>
          <Link href="/dining">ダイニング</Link>
        </div>
        <div className="text-center text-lg">ホテル東京</div>
        <div className="flex items-center justify-end gap-4">
          <Button className="bg-ctm-blue-500 hover:bg-ctm-blue-600" onClick={handleSearch}>
            <SendHorizontal className="w-5 h-5 mr-2" />
            宿泊予約
          </Button>
        </div>
      </nav>
    </div>
  );
};

export default MainNav;