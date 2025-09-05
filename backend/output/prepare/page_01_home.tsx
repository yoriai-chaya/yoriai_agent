import Image from "next/image";

const Home = () => {
  return (
    <div>
      <div className="max-w-2xl mx-auto">
        <Image
          src="/hotel.png"
          alt="ホテルイメージ"
          width={512}
          height={512}
          className="w-full h-auto"
        />
        <h1>都会の静寂に包まれて、心ほどけるひとときを</h1>
        <div>
          東京の中心にありながら、一歩足を踏み入れれば別世界。
          緑に囲まれた静かな空間で、日常の喧騒を忘れ、心からくつろげる時間をお過ごしください。
          四季折々の食材をふんだんに使った料理は、目にも舌にもやさしい贅沢。
          丁寧に仕立てられた一皿一皿が、心と体を満たしてくれます。
          洗練された空間と、温かなもてなしが織りなす、心やすらぐひととき。
          ここは、東京の真ん中にある、あなたの隠れ家です。
        </div>
      </div>
    </div>
  );
};

export default Home;
