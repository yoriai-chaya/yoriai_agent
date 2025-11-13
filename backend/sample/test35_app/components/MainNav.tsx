"use client";
import { House, SendHorizonal } from "lucide-react";
import Link from "next/link";
import { useRouter, usePathname } from "next/navigation";
import { Button } from "@/components/ui/button";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { ModeToggle } from "./ModeToggle";

const MainNav = () => {
  const router = useRouter();
  const pathname = usePathname();

  const handleSearch = async () => {
    console.log("handleSearch called");
    try {
      router.push("/booking/step-1");
    } catch (error) {
      console.error("Error:", error);
    }
  };

  const isHomePage = pathname === "/";

  return (
    <div className="hidden md:flex w-full">
      <nav className="grid grid-cols-3 w-full items-center gap-4">
        {/* A列 */}
        <div className="flex items-center gap-4">
          <Link href="/">
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger>
                  <div className="flex items-center h-10">
                    <House size={20} />
                  </div>
                </TooltipTrigger>
                <TooltipContent side="bottom" className="px-1 py-1 text-[8px]">
                  <p>Home</p>
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>
          </Link>
          <Link
            href="/rooms"
            className="text-ctm-blue-500 hover:underline dark:text-ctm-yellow-200"
          >
            客室
          </Link>
          <Link
            href="/dining"
            className="text-ctm-blue-500 hover:underline dark:text-ctm-yellow-200"
          >
            ダイニング
          </Link>
        </div>
        {/* B列 */}
        <div className="text-center">
          <div className="text-lg text-gray-700 dark:text-gray-100">
            ホテル東京
          </div>
        </div>
        {/* C列 */}
        <div className="flex items-center justify-end gap-4">
          <ModeToggle />
          {isHomePage && (
            <Button
              className="bg-ctm-blue-500 hover:bg-ctm-blue-600 dark:hover:bg-ctm-yellow-200 mr-2"
              onClick={handleSearch}
            >
              <SendHorizonal className="w-5 h-5 mr-2" />
              宿泊予約
            </Button>
          )}
        </div>
      </nav>
    </div>
  );
};

export default MainNav;
