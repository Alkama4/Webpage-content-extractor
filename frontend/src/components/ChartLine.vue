<template>
    <ToggleInput
        v-model="scaleAxisY"
        label="Auto-scale Y-axis"
    />
    <VChart
        ref="chartRef"
        class="chart"
        :manual-update="true"
        autoresize
    />
</template>

<script>
import { use } from "echarts/core";
import { SVGRenderer } from "echarts/renderers";
import { LineChart } from "echarts/charts";
import { TitleComponent, TooltipComponent, LegendComponent, GridComponent, DataZoomComponent } from "echarts/components";
import VChart from "vue-echarts";
import { defineComponent, ref, watch, onMounted } from "vue";
import { formatTimestamp, formatDate } from "@/utils/utils";
import ToggleInput from "./ToggleInput.vue";

use([SVGRenderer, LineChart, TitleComponent, TooltipComponent, LegendComponent, GridComponent, DataZoomComponent]);

export default defineComponent({
    name: "ChartLine",
    components: { VChart, ToggleInput },
    props: {
        chartData: {
            type: Array,
            required: true
        }
    },
    setup(props) {
        const chartRef = ref(null);
        const scaleAxisY = ref(false);

        const updateChart = (data) => {
            // Group data by metric_name
            const seriesMap = {};

            const getColor = idx => palette[idx % palette.length];
            const palette = [
                'hsl(210, 50%, 30%)',
                'hsl(105, 57%, 55%)',
                'hsl(47, 100%, 71%)',
                'hsl(0, 75%, 65%)',
                'hsl(190, 43%, 66%)',
                'hsl(165, 54%, 44%)',
                'hsl(24, 82%, 61%)',
                'hsl(260, 45%, 58%)',
                'hsl(335, 57%, 73%)'
            ];

            data.forEach(item => {
                const key = `${item.metric_name}#${item.element_id}`;
                if (!seriesMap[key]) {
                    // remember the id for later
                    seriesMap[key] = { 
                    name: item.metric_name,          // metric only (for display)
                    elementId: item.element_id,     // keep id separate
                    points: [] 
                    };
                }
                seriesMap[key].points.push({ value: item.value, time: item.created_at });
            });

            const series = Object.values(seriesMap).map((entry, idx) => ({
                name: `${entry.name}#${entry.elementId}`,   // <-- unique per element
                type: 'line',
                smooth: true,
                data: entry.points.map(p => [p.time, p.value]),
                color: getColor(idx)
            }));

            const legendMetrics = [...new Set(series.map(s => s.name))];

            chartRef.value.setOption({
                tooltip: {
                    trigger: "axis",
                    formatter: params => {
                        const time = params[0].axisValue;
                        const rows = params.map(p => `
                            <div style="display:flex; justify-content:space-between; gap:32px;">
                                <span>${p.marker} ${p.seriesName.split("#")[0]}</span>
                                <span">${p.data[1].toLocaleString("fi-FI")}</span>
                            </div>`).join("");

                        return `
                            <div style="font-size: var(--fs-2); font-weight: var(--fw-semibold); color: var(--text-dark-primary); padding-bottom: 4px">
                                ${formatTimestamp(time)}
                            </div>
                            <div style="display:flex; flex-direction:column; gap:2px;">
                                ${rows}
                            </div>`;
                    },
                    borderWidth: 0,
                    extraCssText: `
                        box-shadow: var(--shadow-md);
                        color: var(--text-dark-secondary);
                        font-weight: var(--fw-medium);
                        font-size: var(--fs-1);
                        border-radius: 8px;
                        padding: 10px 12px;
                    `
                },

                textStyle: {
                    fontFamily: "Inter",
                    fontSize: "0.75rem",
                    fontWeight: "500"
                },

                legend: { 
                    data: legendMetrics, 
                    top: 0,
                    formatter: (fullName) => fullName.split("#")[0]
                },
                
                grid: { top: 32, bottom: 110, left: 0, right: 8 },

                xAxis: {
                    type: "time",
                    axisLabel: {
                        formatter: (value) => formatDate(value),
                        rotate: 45,
                        fontSize: "0.75rem",
                        color: "hsl(0, 0%, 45%)"
                    },
                    axisLine: { show: false },
                    axisTick: { show: false }
                },

                yAxis: {
                    type: "value",
                    scale: scaleAxisY.value,
                    axisLabel: {
                        formatter: (v) => v.toLocaleString("fi-FI"),
                        fontSize: "0.75rem",
                        color: "hsl(0, 0%, 45%)", // --text-dark-secondary
                    }
                },

                dataZoom: [
                    {
                        id: 'dataZoomX',
                        type: 'slider',
                        start: 0, 
                        end: 100, 
                        bottom: 8,
                        moveOnMouseMove: true,
                        filterMode: 'filter',
                        backgroundColor: "var(--color-neutral-100)",
                        dataBackground: {
                            areaStyle: {
                                color: "var(--color-neutral-500)"
                            },
                            lineStyle: {
                                color: "var(--color-neutral-500)"
                            }
                        },
                        selectedDataBackground: {
                            areaStyle: {
                                color: "var(--color-primary-500)"
                            },
                            lineStyle: {
                                color: "var(--color-primary-300)"
                            }
                        },
                        fillerColor: "hsla(210, 50%, 50%, 0.15)",
                        borderColor: "var(--color-neutral-300)",
                        handleStyle: {
                            borderColor: "var(--color-primary-300)"
                        },
                        moveHandleStyle: {
                            borderColor: "var(--color-primary-400)"
                        },
                        moveHandleSize: 8,
                        brushStyle: {
                            color: "var(--color-primary-400)"
                        },
                        emphasis: {
                            handleStyle: {
                                borderColor: "var(--color-primary-400)"
                            },
                            moveHandleStyle: {
                                borderColor: "var(--color-primary-400)"
                            }, 
                        }
                    }
                ],

                series
            });
        };

        onMounted(() => {
            if (props.chartData.length) updateChart(props.chartData);
        });

        watch(() => props.chartData, (newData) => {
            if (newData.length) updateChart(newData);
        });

        // use the prop that contains the data array
        watch(scaleAxisY, () => {
          if (props.chartData.length) {
            updateChart(props.chartData);
          }
        });

        return { chartRef, scaleAxisY }
    }
});
</script>

<style scoped>
.chart {
    height: 500px;
    width: 100%;
}
.toggle-input {
    position: absolute;
    right: 32px;
    top: 45px;
    gap: 12px;
}
</style>
