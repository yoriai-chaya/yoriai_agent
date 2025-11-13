import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { Calendar, SendHorizonal } from "lucide-react";

import React from "react";

const SearchAvailableRooms = () => {
  return (
    <Card className="text-gray-700 bg-gray-100 dark:text-gray-100 dark:bg-ctm-navy-700">
      <CardHeader>
        <CardTitle>日付・人数を選択してください</CardTitle>
      </CardHeader>
      <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="flex items-center">
          <span className="mr-5">チェックイン</span>
          <Calendar className="w-5 h-5" />
        </div>
        <div className="flex items-center">
          <span className="mr-5">チェックアウト</span>
          <Calendar className="w-5 h-5" />
        </div>
        <div className="flex items-center">
          <span className="mr-5 text-nowrap">人数</span>
          <Select>
            <SelectTrigger className="ring-0 border-0 shadow-none focus-visible:ring-0">
              <SelectValue placeholder="2人" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="1">1人</SelectItem>
              <SelectItem value="2">2人</SelectItem>
              <SelectItem value="3">3人</SelectItem>
              <SelectItem value="4">4人</SelectItem>
            </SelectContent>
          </Select>
        </div>
        <div className="col-span-1 md:col-span-2 flex justify-center">
          <Button className="bg-ctm-blue-500 hover:bg-ctm-blue-600 dark:hover:bg-ctm-yellow-200 w-full md:w-auto">
            <SendHorizonal className="w-5 h-5 mr-2" />
            空室検索
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};

export default SearchAvailableRooms;
