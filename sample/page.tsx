"use client"
import Image from 'next/image';
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";

const Home = () => {
  const router = useRouter();

  const handleSearch = () => {
    router.push('/booking/step-1');
  };

  return (
    <div className="max-w-2xl mx-auto pb-16" data-testid="home-container">
      <Image
        src="/hotel.png"
        alt="Hotel Image"
        width={512}
        height={512}
        className="w-full h-auto"
        data-testid="home-hero-image"
      />
      <h1 className="text-lg font-bold text-center" data-testid="home-title">
        都会の静寂に包まれて、心ほどけるひとときを
      </h1>
      <div className="text-sm px-8" data-testid="home-description">
        <div>東京の中心にありながら、一歩足を踏み入れれば別世界。緑に囲まれた静かな空間で、日常の喧騒を忘れ、心からくつろげる時間をお過ごしください。四季折々の食材をふんだんに使った料理は、目にも舌にもやさしい贅沢。丁寧に仕立てられた一皿一皿が、心と体を満たしてくれます。洗練された空間と、温かなもてなしが織りなす、心やすらぐひととき。ここは、東京の真ん中にある、あなたの隠れ家です。</div>
      </div>
      <Button
        className="fixed bottom-4 justify-center md:hidden bg-ctm-blue-500 hover:bg-ctm-blue-600 z-50"
        onClick={handleSearch}
        data-testid="mobile-booking-button"
      >
        宿泊予約
      </Button>
    </div>
  );
};

export default Home;