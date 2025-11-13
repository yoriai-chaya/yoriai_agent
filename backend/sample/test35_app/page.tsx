"use client";
import { Button } from "@/components/ui/button";
import { SendHorizonal } from "lucide-react";

import { useRouter } from "next/navigation";
import Image from "next/image";

export default function Home() {
  const router = useRouter();

  const handleSearch = async () => {
    console.log("handleSearch called");
    try {
      router.push("/booking/step-1");
    } catch (error) {
      console.error("Error:", error);
    }
  };

  return (
    <div className="flex flex-col pb-16">
      <div className="relative w-full aspect-[800/543]">
        <Image
          src="/hotel.png"
          alt="hotel"
          fill
          className="object-contain"
          sizes="100vw"
        />
      </div>
      <h1 className="text-center text-lg px-8 pb-4 text-gray-700 dark:text-gray-100">
        都会の静寂に包まれて、心ほどけるひとときを
      </h1>
      <div className="text-left text-sm px-8 text-gray-500">
        東京の中心にありながら、一歩足を踏み入れれば別世界。
        緑に囲まれた静かな空間で、日常の喧騒を忘れ、心からくつろげる時間をお過ごしください。
        四季折々の食材をふんだんに使った料理は、目にも舌にもやさしい贅沢。
        丁寧に仕立てられた一皿一皿が、心と体を満たしてくれます。洗練された空間と、温かなもてなしが織りなす、心やすらぐひととき。
        ここは、東京の真ん中にある、あなたの隠れ家です。
      </div>
      <div className="fixed bottom-4 left-0 right-0 flex justify-center md:hidden z-50">
        <Button
          className="bg-ctm-blue-500 hover:bg-ctm-blue-600 dark:hover:bg-ctm-yellow-200 mr-2"
          onClick={handleSearch}
        >
          <SendHorizonal className="w-5 h-5 mr-2" />
          宿泊予約
        </Button>
      </div>
    </div>
  );
}
