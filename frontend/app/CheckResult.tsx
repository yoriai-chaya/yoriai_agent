import React from "react";
import { CheckResultItem } from "./types";

interface CheckResultProps {
  checkResults: CheckResultItem[];
}

const CheckResult = ({ checkResults }: CheckResultProps) => {
  return (
    <>
      {checkResults.map((ev, idx) => {
        const { result, rule_id } = ev.s_res.payload;

        return (
          <div key={`check-${idx}`}>
            {!result && <div className="ml-6">{rule_id}</div>}
          </div>
        );
      })}
    </>
  );
};

export default CheckResult;
