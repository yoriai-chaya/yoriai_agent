"use client"
import React from 'react';
import { SendHorizontal } from "lucide-react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { useRouter, usePathname } from "next/navigation";

const MainNav = () => {
  const router = useRouter();
  const pathname = usePathname();

  const handleSearch = () => {
    router.push('/booking/step-1');
  };

  return (
    <div data-testid="main-nav" className="hidden md:flex w-full">
      <nav className="grid grid-cols-3 w-full items-center gap-4">
        <div className="flex items-center gap-4">
          <Link href="/rooms" data-testid="main-navbar-link-rooms">客室</Link>
          <Link href="/dining" data-testid="main-navbar-link-dining">ダイニング</Link>
        </div>
        <div className="text-center text-lg" data-testid="main-navbar-title">ホテル東京</div>
        <div className="flex items-center justify-end gap-4">
          {pathname === '/' && (
            <Button
              className="bg-ctm-blue-500 hover:bg-ctm-blue-600"
              onClick={handleSearch}
              data-testid="main-navbar-button-booking"
            >
              <SendHorizontal className="w-5 h-5 mr-2" />
              宿泊予約
            </Button>
          )}
        </div>
      </nav>
    </div>
  );
};

export default MainNav;