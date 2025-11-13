<template>
    <div>
        <div 
            class="log-entry" 
            :class="{'webpage': log?.webpage_id, 'element': log?.element_id}" 
            @click="showElementListing = !showElementListing"
        >
            <div class="flex-row space-between vertical-align">
                <div class="flex-col">
                    <div class="flex-row vertical-align gap-8">
                        <div class="status" :class="log?.status">{{ toTitleCase(log.status) }}</div>
                        <div>
                            {{ log.webpage_id ? 'Webpage' : 'Element'}}
                            #{{ log.webpage_id || log.element_id }}
                        </div>
                        <div>({{ formatTimestamp(log.attempted_at) }})</div>
                    </div>
                    <div class="message">
                        {{ log.message.replace("; ", "\n") }}
                    </div>
                </div>
                <div class="controls flex-row">
                    <a 
                        :href="log.webpage_id 
                            ? `/webpages/${log.webpage_id}`
                            : `/webpages/${parentWebpageId}/elements/${log.element_id}`
                        " 
                        target="_blank"
                    >
                        <i class="btn btn-transp btn-icon bx bx-link-external"></i>
                    </a>
                </div>
            </div>
        </div>

        <transition
            name="element-fade"
            @enter="enter"
            @leave="leave"
        >
            <div
                v-if="showElementListing && log.webpage_id"
                ref="elementWrapper"
                class="element-wrapper"
            >
                <div v-if="log.elements.length > 0" class="log-entry-wrapper">
                    <LogEntry
                        v-for="elementLog in log.elements"
                        :log="elementLog"
                        :parentWebpageId="log.webpage_id"
                        :key="elementLog.element_log_id"
                    />
                </div>
                <div v-else class="listing-placeholder-wrapper">
                    <ListingPlaceholder
                        icon="bx bxs-file"
                        text="No element logs found"
                        desc="There were no elements scraped during the scrape."
                    />
                </div>
            </div>
        </transition>
    </div>
</template>

<script>
import { formatTimestamp } from '@/utils/utils';
import ListingPlaceholder from './ListingPlaceholder.vue';

export default {
    name: 'LogEntry',
    props: {
        log: {
            type: Array,
            required: true
        },
        parentWebpageId: {
            type: Number,
            required: false
        }
    },
    components: {
        ListingPlaceholder
    },
    data() {
        return {
            showElementListing: false,
            wrapperHeight: 100,
        }
    },
    methods: {
        formatTimestamp(timestamp) {
            return formatTimestamp(timestamp);
        },
        toTitleCase(str) {
            return str.replace(/\b\w/g, char => char.toUpperCase());
        },
        enter(el) {
            el.style.height = '0px';
            const targetHeight = el.scrollHeight + 'px';
            requestAnimationFrame(() => {
                el.style.transition = 'all var(--t-slow)';
                el.style.height = targetHeight;
            });
        },
        leave(el) {
            el.style.height = el.scrollHeight + 'px';
            requestAnimationFrame(() => {
                el.style.transition = 'all var(--t-slow)';
                el.style.height = '0px';
            });
        }
    }
}
</script>

<style scoped>
.log-entry {
    display: flex;
    align-items: center;
    gap: 8px;
    width: 100%;
    box-sizing: border-box;
    padding: 12px 16px;
    transition: all var(--t-fast);
}

.log-entry.webpage {
    background: var(--color-neutral-100);
    cursor: pointer;
    border: 1px solid transparent;
    box-shadow: var(--shadow-xs);
    border-radius: var(--btn-radius);
}
.log-entry.webpage:hover {
    background: var(--color-neutral-50);
    box-shadow: var(--shadow-sm);
    transform: translateY(var(--btn-translate));
}

.log-entry.element {
    /* border-top: 2px solid var(--color-neutral-300); */
}


div.status {
    border-radius: 12px;
    color: var(--text-light-primary);
    padding: 1px 8px;
    font-size: var(--fs-1);

}
div.status.success {
    background-color: var(--color-success);
}
div.status.partial {
    background-color: var(--color-warning);
}
div.status.failure {
    background-color: var(--color-error);
}

.message {
    padding-top: 8px;
    color: var(--text-dark-secondary);
    white-space: pre-line; 
    line-height: 2ch;
}

.element-wrapper {
    overflow: hidden;
}

.log-entry-wrapper {
    margin: 8px 0;
}

.listing-placeholder-wrapper {
    margin: 16px 0;
    filter: grayscale(1);
}
</style>