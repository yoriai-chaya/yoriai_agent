import SearchAvailableRooms from "@/app/components/SearchAvailableRooms";

export default function Home() {
  return (
    <div className="flex flex-col items-center">
      <div className="w-full max-w-md">
        <SearchAvailableRooms />
      </div>
    </div>
  );
}
