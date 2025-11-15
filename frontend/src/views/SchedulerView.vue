<template>
    <div class="scheduler-view">
        <h1>Scheduler</h1>
        <div class="scheduler-view-grid gap-16">
            <CardBasic
                icon="bx-list-ul"
                title="Disabled Webpages" 
                description="Webpages that aren't currently set to scrape."
            >
                <div class="vertical-scroll-list" v-if="availableWebpages.length > 0">
                    <ListEntry
                        v-for="webpage in availableWebpages"
                        :key="webpage.webpage_id"
                        :item="webpage"
                        :to="`/webpages/${webpage.webpage_id}`"
                        icon="bx bx-globe"
                        :label="webpage.page_name"
                        :description="`${formatScheduleTime(webpage)} - Disabled`"
                        :actions="[
                            {
                                icon: 'bx bx-time-five',
                                method: adjustSchedule
                            },
                            {
                                icon: 'bx bx-right-arrow-alt',
                                method: scheduleWebpage
                            }
                        ]"
                    />
                </div>
                <ListingPlaceholder 
                    v-else
                    icon="bx-globe"
                    text="No scheduled webpages"
                    desc="All of the webpages are currently scheduled."
                />
            </CardBasic>

            <CardBasic
                icon="bx-time-five"
                title="Scheduled Webpages" 
                description="Webpages that will be scraped at the scheduled time."
            >
                <div class="vertical-scroll-list" v-if="scheduledWebpages.length > 0">
                    <ListEntry
                        v-for="webpage in scheduledWebpages"
                        :key="webpage.webpage_id"
                        :item="webpage"
                        :to="`/webpages/${webpage.webpage_id}`"
                        icon="bx bx-globe"
                        :label="webpage.page_name"
                        :description="`${formatScheduleTime(webpage)} - Enabled`"
                        :actions="[
                            {
                                icon: 'bx bx-time-five',
                                method: adjustSchedule
                            },
                            {
                                icon: 'bx bx-left-arrow-alt',
                                method: unscheduleWebpage
                            }
                        ]"
                    />
                </div>
                <ListingPlaceholder 
                    v-else
                    icon="bx-time-five"
                    text="No scheduled webpages"
                    desc="You can schedule your webpages from the left so that they appear here."
                />
            </CardBasic>
        </div>
        
        <ModalSchedule ref="ModalScheduleRef"/>
    </div>
</template>

<script>
import CardBasic from '@/components/CardBasic.vue';
import ListEntry from '@/components/ListEntry.vue';
import ListingPlaceholder from '@/components/ListingPlaceholder.vue';
import { fastApi } from '@/utils/fastApi';
import ModalBasic from '@/components/ModalBasic.vue';
import ModalSchedule from '@/components/ModalSchedule.vue';
import { formatScheduleTime } from '@/utils/utils';

export default {
    name: 'SchedulerView',
    components: {
        CardBasic,
        ListEntry,
        ListingPlaceholder,
        ModalBasic,
        ModalSchedule,
    },
        data() {
            return {
                availableWebpages: [],
                scheduledWebpages: [],
                selectedWebpage: null,
                showScheduleModal: false,
                showScheduleInfo: false,
                showDeleteModal: false
            };
        },
            methods: {
                formatScheduleTime(webpage) {
                    return formatScheduleTime(webpage.run_time)
                },
                async fetchWebpages() {
                    try {
                        // Fetch all webpages
                        const allWebpages = await fastApi.webpages.get();
                        console.log('All webpages from API:', allWebpages);
                        
                        if (allWebpages) {
                            // Check if is_enabled field exists and its values
                            allWebpages.forEach(webpage => {
                                console.log(`Webpage ${webpage.webpage_id}: is_enabled = ${webpage.is_enabled} (type: ${typeof webpage.is_enabled})`);
                            });
                            
                            // Filter available webpages (is_enabled = false or undefined/null)
                            this.availableWebpages = allWebpages.filter(webpage => 
                                webpage.is_enabled === false || webpage.is_enabled === undefined || webpage.is_enabled === null
                            );
                            console.log('Available webpages:', this.availableWebpages);
                            
                            // Filter scheduled webpages (is_enabled = true)
                            this.scheduledWebpages = allWebpages.filter(webpage => webpage.is_enabled === true);
                            console.log('Scheduled webpages:', this.scheduledWebpages);
                        }
                    } catch (error) {
                        console.error('Error fetching webpages:', error);
                    }
                },
                async scheduleWebpage(webpage) {
                    try {
                        // Update webpage to scheduled (is_enabled = true)
                        await fastApi.webpages.patch(webpage.webpage_id, { is_enabled: true });
                        
                        // Update the webpage object in place for immediate UI feedback
                        webpage.is_enabled = true;
                        
                        // Refresh the lists
                        await this.fetchWebpages();
                    } catch (error) {
                        console.error('Error scheduling webpage:', error);
                    }
                },
                async unscheduleWebpage(webpage) {
                    try {
                        // Update webpage back to available (is_enabled = false)
                        await fastApi.webpages.patch(webpage.webpage_id, { is_enabled: false });
                        
                        // Update the webpage object in place for immediate UI feedback
                        webpage.is_enabled = false;
                        
                        // Refresh the lists
                        await this.fetchWebpages();
                    } catch (error) {
                        console.error('Error unscheduling webpage:', error);
                    }
                },
                async adjustSchedule(webpage) {
                    const response = await this.$refs.ModalScheduleRef.open(webpage);
                    if (response && response.success) {
                        await this.fetchWebpages();
                    } 
                }
            },
    async mounted() {
        await this.fetchWebpages()
    },
};
</script>

<style scoped>
.scheduler-view {
    /* max-width: 1200px; */
    margin: 0 auto;
}

.scheduler-view-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 2rem;
    margin-top: 2rem;
}

@media(max-width: 1000px) {
    .scheduler-view-grid {
        grid-template-columns: 1fr;
        gap: 1.5rem;
    }
}

</style>
