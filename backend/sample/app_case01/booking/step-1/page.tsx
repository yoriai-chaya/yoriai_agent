"use client"
import { useState } from "react";
import { SendHorizontal } from "lucide-react";
import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { DatePicker } from '@/components/ui/date-picker';
import { Select, SelectTrigger, SelectContent, SelectItem, SelectValue } from '@/components/ui/select';

const BookingStep1 = () => {
  const [checkInDate, setCheckInDate] = useState<Date | undefined>(undefined);
  const [checkOutDate, setCheckOutDate] = useState<Date | undefined>(undefined);
  const [guests, setGuests] = useState<number>(2);

  return (
    <div className="flex flex-col items-center p-2">
      <div className="w-full max-w-md">
        <Card className="bg-gray-100 text-gray-700">
          <CardHeader>
            <CardTitle data-testid="booking-step1-title">日付・人数を選択してください</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-4">
              <div className="flex flex-col items-center">
                <span data-testid="checkin-title">チェックイン</span>
                <DatePicker date={checkInDate} setDate={setCheckInDate} name="check-in" />
              </div>
              <div className="flex flex-col items-center">
                <span data-testid="checkout-title">チェックアウト</span>
                <DatePicker date={checkOutDate} setDate={setCheckOutDate} name="check-out" />
              </div>
              <div className="flex items-center">
                <span className="mx-5 whitespace-nowrap">人数</span>
                <Select value={guests.toString()} onValueChange={(v) => setGuests(Number(v))}>
                  <SelectTrigger className="ring-0 focus-visible:ring-0 border-0 shadow-none" data-testid="guest-select-trigger">
                    <SelectValue placeholder="人数を選択" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="1" data-testid="guest-option-1">1人</SelectItem>
                    <SelectItem value="2" data-testid="guest-option-2">2人</SelectItem>
                    <SelectItem value="3" data-testid="guest-option-3">3人</SelectItem>
                    <SelectItem value="4" data-testid="guest-option-4">4人</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="flex col-span-2 justify-center">
                <Button className="bg-ctm-blue-500 hover:bg-ctm-blue-600 w-full md:w-auto" data-testid="room-search">
                  <SendHorizontal className="w-5 h-5 mr-2" />
                  空室検索
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default BookingStep1;

