import React, { forwardRef } from "react";
import { Chart as ChartJS } from "chart.js";
import type { ChartType, ChartComponentLike } from "chart.js";
import { CandlestickController } from "chartjs-chart-financial";

import {
  ChartProps,
  ChartJSOrUndefined,
  TypedChartComponent,
} from "react-chartjs-2/dist/types";
import { Chart } from "react-chartjs-2";

function createTypedChart<T extends ChartType>(
  type: T,
  registerables: ChartComponentLike,
) {
  ChartJS.register(registerables);

  return forwardRef<ChartJSOrUndefined<T>, Omit<ChartProps<T>, "type">>(
    (props, ref) => <Chart {...props} ref={ref} type={type} />,
  ) as TypedChartComponent<T, true>;
}

export const Candlestick = /* #__PURE__ */ createTypedChart(
  "candlestick",
  CandlestickController,
);
