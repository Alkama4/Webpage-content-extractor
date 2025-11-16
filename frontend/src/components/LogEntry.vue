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
                        <label>
                            {{ log.page_name ?? log.metric_name }}
                        </label>
                    </div>
                    <span class="details">
                        <span class="type-id">
                            {{ log.webpage_id ? 'Webpage ID' : 'Element ID'}}
                            #{{ log.webpage_id || log.element_id }}
                        </span>
                        -
                        <span>{{ formatTimestamp(log.attempted_at) }}</span>
                    </span>
                    <div class="message">
                        {{ log.message }}
                    </div>
                </div>
                <div class="controls flex-row" v-if="enableTopLevelLinks">
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
                    <!-- <div class="seperator"></div> -->
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
        },
        enableTopLevelLinks: {
            type: Boolean,
            default: true
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
    flex-direction: column;
    /* align-items: center; */
    /* gap: 8px; */
    width: 100%;
    box-sizing: border-box;
    padding: 16px;
    transition: all var(--t-fast);
    border-radius: var(--btn-radius);
    background: var(--color-neutral-100);
    box-shadow: var(--shadow-sm);
}

.log-entry.webpage {
    cursor: pointer;
}
.log-entry.webpage:hover {
    background: var(--color-neutral-50);
    box-shadow: var(--shadow-md);
    transform: translateY(var(--btn-translate));
}


/* .log-entry.element {
    background-color: red;
} */
.log-entry .log-entry.element {
    /* border-top: 2px solid var(--color-neutral-300); */
    background-color: hsla(0, 0%, 0%, 0.045);
    box-shadow: unset;
}


div.status {
    border-radius: 12px;
    color: var(--text-light-primary);
    padding: 0px 8px;
    font-size: var(--fs-0);

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

label {
    cursor: pointer;
    font-weight: var(--fw-medium);
    font-size: var(--fs-2);
    color: var(--text-dark-primary);
}

.details {
    color: var(--text-dark-secondary);
    font-size: var(--fs-1);
}

.message {
    padding-top: 0px;
    white-space: pre-line; 
    line-height: 2ch;
}

.element-wrapper {
    overflow: hidden;
    /* margin-left: 32px; */

}

.element-wrapper .seperator {
    height: 2px;
    margin: 8px 0;
    width: 100%;
    background-color: var(--color-neutral-300);
    border-radius: 100px;
}

.log-entry-wrapper {
    margin-top: 16px;
    /* margin: 0px -16px; */
    /* background-color: hsla(0, 0%, 0%, 0.065); */
    border-radius: 8px;
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.listing-placeholder-wrapper {
    margin: 16px 0;
}
</style>