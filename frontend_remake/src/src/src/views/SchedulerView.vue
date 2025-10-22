<template>
    <div class="scheduler-view">
        <h1>Scheduler</h1>
        <div class="scheduler-view-grid gap-16">
            <BasicCard
                icon="bx-list-ul"
                title="Available Webpages" 
                description="Select webpages to schedule scraping"
            >
                <div class="entry-list-wrapper" v-if="availableWebpages.length > 0">
                    <div 
                        v-for="webpage in availableWebpages"
                        :key="webpage.webpage_id"
                        class="scheduler-webpage-item"
                        :class="{ 'locked': webpage.is_active === false }"
                    >
                        <div class="webpage-info">
                            <div class="webpage-name">{{ webpage.page_name }}</div>
                            <div class="webpage-url">{{ webpage.url }}</div>
                        </div>
                        <button 
                            @click="scheduleWebpage(webpage)"
                            class="schedule-btn"
                            :disabled="webpage.is_active === false"
                        >
                            <i class="bx" :class="webpage.is_active === false ? 'bx-lock' : 'bx-time-five'"></i>
                            {{ webpage.is_active === false ? 'Scheduled' : 'Schedule' }}
                        </button>
                    </div>
                </div>
                <ListingPlaceholder 
                    v-else
                    icon="bx-globe"
                    text="No available webpages"
                    desc="All webpages are already scheduled or create new ones."
                />
            </BasicCard>

            <BasicCard
                icon="bx-time-five"
                title="Scheduled Webpages" 
                description="Manage scheduled scraping tasks"
            >
                <div class="entry-list-wrapper" v-if="scheduledWebpages.length > 0">
                    <div 
                        v-for="webpage in scheduledWebpages"
                        :key="webpage.webpage_id"
                        class="scheduler-webpage-item"
                    >
                        <div class="webpage-info">
                            <div class="webpage-name">{{ webpage.page_name }}</div>
                            <div class="webpage-url">{{ webpage.url }}</div>
                        </div>
                        <button 
                            @click="unscheduleWebpage(webpage)"
                            class="schedule-btn"
                        >
                            <i class="bx bx-x"></i>
                            Unschedule
                        </button>
                    </div>
                </div>
                <ListingPlaceholder 
                    v-else
                    icon="bx-time-five"
                    text="No scheduled webpages"
                    desc="Schedule webpages from the left to manage them here."
                />
                
                <div class="scheduling-content" v-if="selectedWebpage">
                    <div class="selected-webpage-container">
                        <div class="webpage-title-section" @click="toggleScheduleInfo">
                            <h3 class="webpage-title">{{ selectedWebpage.page_name }}</h3>
                            <div class="title-actions">
                                <i class="bx" :class="showScheduleInfo ? 'bx-chevron-up' : 'bx-chevron-down'"></i>
                            </div>
                        </div>
                        
                        <div v-if="showScheduleInfo">
                            <div class="date-time-content">
                                <div class="time-info">
                                    <i class="bx bx-time"></i>
                                    <span class="info-label">Time:</span>
                                    <span class="info-value">9:00 AM</span>
                                </div>
                                <div class="day-info">
                                    <i class="bx bx-repeat"></i>
                                    <span class="info-label">Freq:</span>
                                    <span class="info-value">Every day</span>
                                </div>
                            </div>
                            
                            <div class="bottom-row">
                                <div class="schedule-details-section" @click="openScheduleModal">
                                    <i class="bx bx-info-circle"></i>
                                    <span>INFO</span>
                                </div>
                                
                                <button @click="clearSelection" class="clear-btn">
                                    <i class="bx bxs-trash"></i>
                                    <span>DELETE</span>
                                </button>
                            </div>
                        </div>
                    </div>
                    
                    <div class="scheduling-form">
                        <h4>Scheduling Configuration</h4>
                        <p class="form-description">Configure when and how often to scrape this webpage.</p>
                        <div class="form-placeholder">
                            <i class="bx bx-time-five"></i>
                            <span>Scheduling options will be implemented here</span>
                        </div>
                    </div>
                </div>
                <div class="scheduling-content" v-else>
                    <p class="no-selection">Select a webpage from the left to configure scheduling.</p>
                </div>
            </BasicCard>
        </div>
        
        <!-- Schedule Details Modal -->
        <div v-if="showScheduleModal" class="schedule-modal" @click="closeScheduleModal">
            <div class="modal-content" @click.stop>
                <div class="modal-header">
                    <h3>Schedule Details</h3>
                    <button @click="closeScheduleModal" class="modal-close">
                        <i class="bx bx-x"></i>
                    </button>
                </div>
                <div class="modal-body">
                    <div class="detail-section">
                        <h4>Webpage Information</h4>
                        <div class="detail-item">
                            <i class="bx bx-globe"></i>
                            <div class="detail-content">
                                <span class="detail-label">URL</span>
                                <span class="detail-value">{{ selectedWebpage?.url }}</span>
                            </div>
                        </div>
                    </div>
                    <div class="detail-section">
                        <h4>Timing</h4>
                        <div class="detail-item">
                            <i class="bx bx-time"></i>
                            <div class="detail-content">
                                <span class="detail-label">Time</span>
                                <span class="detail-value">9:00 AM</span>
                            </div>
                        </div>
                    </div>
                    <div class="detail-section">
                        <h4>Date Range</h4>
                        <div class="detail-item">
                            <i class="bx bx-calendar"></i>
                            <div class="detail-content">
                                <span class="detail-label">Start Date</span>
                                <span class="detail-value">January 15, 2024</span>
                            </div>
                        </div>
                        <div class="detail-item">
                            <i class="bx bx-calendar-check"></i>
                            <div class="detail-content">
                                <span class="detail-label">End Date</span>
                                <span class="detail-value">No end date (Continuous)</span>
                            </div>
                        </div>
                    </div>
                    <div class="detail-section">
                        <h4>Frequency</h4>
                        <div class="detail-item">
                            <i class="bx bx-repeat"></i>
                            <div class="detail-content">
                                <span class="detail-label">Frequency</span>
                                <span class="detail-value">Every day</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Confirmation Modal -->
        <div v-if="showDeleteModal" class="modal-overlay" @click="closeDeleteModal">
            <div class="modal-content" @click.stop>
                <div class="modal-header">
                    <h3>Confirm Deletion</h3>
                    <button @click="closeDeleteModal" class="modal-close">
                        <i class="bx bx-x"></i>
                    </button>
                </div>
                <div class="modal-body">
                    <p>Are you sure you want to delete the schedule for <strong>{{ selectedWebpage?.page_name }}</strong>?</p>
                    <div class="modal-actions">
                        <button @click="closeDeleteModal" class="btn-cancel">Cancel</button>
                        <button @click="confirmDelete" class="btn-delete">Delete</button>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import BasicCard from '@/components/CardBasic.vue';
import ListEntry from '@/components/ListEntry.vue';
import ListingPlaceholder from '@/components/ListingPlaceholder.vue';
import { fastApi } from '@/utils/fastApi';

export default {
    name: 'SchedulerView',
    components: {
        BasicCard,
        ListEntry,
        ListingPlaceholder,
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
                async fetchWebpages() {
                    try {
                        // Fetch all webpages
                        const allWebpages = await fastApi.webpages.get();
                        console.log('All webpages from API:', allWebpages);
                        
                        if (allWebpages) {
                            // Check if is_active field exists and its values
                            allWebpages.forEach(webpage => {
                                console.log(`Webpage ${webpage.webpage_id}: is_active = ${webpage.is_active} (type: ${typeof webpage.is_active})`);
                            });
                            
                            // Filter available webpages (is_active = true or undefined/null)
                            this.availableWebpages = allWebpages.filter(webpage => 
                                webpage.is_active === true || webpage.is_active === undefined || webpage.is_active === null
                            );
                            console.log('Available webpages:', this.availableWebpages);
                            
                            // Filter scheduled webpages (is_active = false)
                            this.scheduledWebpages = allWebpages.filter(webpage => webpage.is_active === false);
                            console.log('Scheduled webpages:', this.scheduledWebpages);
                        }
                    } catch (error) {
                        console.error('Error fetching webpages:', error);
                    }
                },
                async scheduleWebpage(webpage) {
                    try {
                        // Update webpage to scheduled (is_active = false)
                        await fastApi.webpages.patch(webpage.webpage_id, { is_active: false });
                        
                        // Update the webpage object in place for immediate UI feedback
                        webpage.is_active = false;
                        
                        // Refresh the lists
                        await this.fetchWebpages();
                    } catch (error) {
                        console.error('Error scheduling webpage:', error);
                    }
                },
                async unscheduleWebpage(webpage) {
                    try {
                        // Update webpage back to available (is_active = true)
                        await fastApi.webpages.patch(webpage.webpage_id, { is_active: true });
                        
                        // Update the webpage object in place for immediate UI feedback
                        webpage.is_active = true;
                        
                        // Refresh the lists
                        await this.fetchWebpages();
                    } catch (error) {
                        console.error('Error unscheduling webpage:', error);
                    }
                },
                clearSelection() {
                    this.showDeleteModal = true;
                },
                async confirmDelete() {
                    try {
                        if (this.selectedWebpage) {
                            // Update webpage back to available (is_active = 1)
                            await fastApi.webpages.patch(this.selectedWebpage.webpage_id, { is_active: 1 });
                            this.selectedWebpage = null;
                            // Refresh the webpage lists
                            await this.fetchWebpages();
                        }
                        this.showDeleteModal = false;
                    } catch (error) {
                        console.error('Error unscheduling webpage:', error);
                    }
                },
                closeDeleteModal() {
                    this.showDeleteModal = false;
                },
                openScheduleModal() {
                    this.showScheduleModal = true;
                },
                closeScheduleModal() {
                    this.showScheduleModal = false;
                },
                toggleScheduleInfo() {
                    this.showScheduleInfo = !this.showScheduleInfo;
                }
            },
    async mounted() {
        await this.fetchWebpages()
    },
};
</script>

<style scoped>
.scheduler-view {
    max-width: 1200px;
    margin: 0 auto;
}

.scheduler-view h1 {
    font-size: var(--fs-8);
    font-weight: var(--fw-bold);
    color: var(--text-dark-primary);
    margin-bottom: 0.5rem;
    background: linear-gradient(135deg, var(--color-primary-600), var(--color-primary-500));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
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

.scheduling-content {
    padding: 1rem 0;
    color: var(--text-dark-secondary);
    font-style: italic;
}

.scheduler-webpage-item {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 0.5rem;
    padding: 12px 16px;
    background: var(--color-neutral-100);
    border: 1px solid var(--color-neutral-200);
    border-radius: var(--btn-radius);
    box-shadow: var(--shadow-xs);
}

.scheduler-webpage-item.locked {
    background: var(--color-neutral-200);
    border-color: var(--color-neutral-300);
    opacity: 0.7;
}

.webpage-info {
    flex: 1;
}

.webpage-name {
    font-weight: var(--fw-medium);
    font-size: var(--fs-2);
    color: var(--text-dark-primary);
    margin-bottom: 2px;
}

.webpage-url {
    font-size: var(--fs-1);
    color: var(--text-dark-secondary);
}

.schedule-btn {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 8px 12px;
    border-radius: 12px;
    background: var(--color-primary-500);
    color: var(--text-light-primary);
    border: none;
    font-size: var(--fs-1);
    font-weight: var(--fw-medium);
    cursor: pointer;
    transition: all var(--t-fast);
    white-space: nowrap;
}


.schedule-btn:disabled {
    background: var(--color-neutral-400);
    cursor: not-allowed;
}

.selected-webpage-container {
    background: var(--color-neutral-50);
    border: 1px solid var(--color-neutral-200);
    border-radius: 12px;
    padding: 1.5rem;
    box-shadow: var(--shadow-sm);
    margin-bottom: 1rem;
}

.webpage-title-section {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 1rem;
    cursor: pointer;
    padding: 0.75rem;
    background: var(--color-neutral-100);
    border-radius: 8px;
    border: 1px solid var(--color-neutral-200);
    transition: all var(--t-fast);
}

.webpage-title-section:hover {
    background: var(--color-neutral-200);
}

.webpage-title {
    margin: 0;
    color: var(--text-dark-primary);
    font-size: var(--fs-4);
    font-weight: var(--fw-bold);
    text-align: center;
    flex: 1;
}

.title-actions {
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.webpage-url-section {
    margin-bottom: 1rem;
    padding: 0.75rem;
    background: var(--color-neutral-100);
    border-radius: 8px;
    border: 1px solid var(--color-neutral-200);
}

.url-label {
    color: var(--text-dark-tertiary);
    font-size: var(--fs-1);
    font-weight: var(--fw-medium);
    margin-right: 0.5rem;
}

.url-value {
    color: var(--text-dark-primary);
    font-size: var(--fs-2);
    font-weight: var(--fw-medium);
    word-break: break-all;
    user-select: none;
    -webkit-user-select: none;
    -moz-user-select: none;
    -ms-user-select: none;
}

.date-time-section {
    margin-bottom: 1rem;
}

.date-time-header {
    display: flex;
    align-items: center;
    padding: 0.75rem;
    background: var(--color-neutral-100);
    border-radius: 8px;
    border: 1px solid var(--color-neutral-200);
    margin-bottom: 1rem;
}

.date-time-header span {
    color: var(--text-dark-primary);
    font-size: var(--fs-2);
    font-weight: var(--fw-semibold);
}

.date-time-content {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
    margin-bottom: 1rem;
}

.schedule-details-section {
    background: hsl(210, 50%, 30%);
    border: 1px solid hsl(210, 50%, 30%);
    border-radius: 20px;
    padding: 0.75rem 1rem;
    cursor: pointer;
    transition: all var(--t-fast);
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    height: 48px;
    box-sizing: border-box;
    box-shadow: var(--shadow-xs);
}

.schedule-details-section:hover {
    background: hsl(210, 50%, 25%);
    border-color: hsl(210, 50%, 25%);
    transform: none;
    box-shadow: var(--shadow-sm);
}

.schedule-details-section span {
    color: var(--text-light-primary) !important;
    font-weight: var(--fw-semibold);
    font-size: var(--fs-2);
}

.schedule-details-section i {
    color: var(--text-light-primary) !important;
    font-size: var(--fs-3);
}

.bottom-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
    margin-top: 1rem;
}

.bottom-row .clear-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    padding: 0.75rem 1rem;
    border-radius: 20px;
    background: hsl(210, 50%, 30%);
    color: var(--text-light-primary);
    border: 1px solid hsl(210, 50%, 30%);
    cursor: pointer;
    transition: all var(--t-fast);
    font-size: var(--fs-2);
    font-weight: var(--fw-semibold);
    box-shadow: var(--shadow-xs);
    width: 100%;
    height: 48px;
    box-sizing: border-box;
}

.bottom-row .clear-btn:hover {
    background: hsl(210, 50%, 25%);
    border-color: hsl(210, 50%, 25%);
    transform: none;
    box-shadow: var(--shadow-sm);
}

.scheduling-details:hover {
    border-color: var(--color-primary-300);
    box-shadow: var(--shadow-md);
}

/* Confirmation Modal */
.modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
}

.modal-content {
    background: var(--color-neutral-50);
    border-radius: 12px;
    box-shadow: var(--shadow-lg);
    max-width: 400px;
    width: 90%;
    max-height: 90vh;
    overflow: hidden;
}

.modal-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1.5rem 1.5rem 1rem;
    border-bottom: 1px solid var(--color-neutral-200);
}

.modal-header h3 {
    margin: 0;
    font-size: var(--fs-4);
    font-weight: var(--fw-bold);
    color: var(--text-dark-primary);
}

.modal-close {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 32px;
    height: 32px;
    border-radius: 8px;
    background: var(--color-neutral-200);
    color: var(--text-dark-secondary);
    border: none;
    cursor: pointer;
    transition: all var(--t-fast);
}

.modal-close:hover {
    background: var(--color-neutral-300);
    color: var(--text-dark-primary);
}

.modal-body {
    padding: 1.5rem;
}

.modal-body p {
    margin: 0 0 1.5rem;
    color: var(--text-dark-secondary);
    line-height: 1.5;
}

.modal-actions {
    display: flex;
    gap: 1rem;
    justify-content: flex-end;
}

.btn-cancel {
    padding: 0.75rem 1.5rem;
    border-radius: 8px;
    background: var(--color-neutral-200);
    color: var(--text-dark-primary);
    border: 1px solid var(--color-neutral-300);
    cursor: pointer;
    transition: all var(--t-fast);
    font-size: var(--fs-2);
    font-weight: var(--fw-medium);
}

.btn-cancel:hover {
    background: var(--color-neutral-300);
    border-color: var(--color-neutral-400);
}

.btn-delete {
    padding: 0.75rem 1.5rem;
    border-radius: 8px;
    background: var(--color-error);
    color: var(--text-light-primary);
    border: 1px solid var(--color-error);
    cursor: pointer;
    transition: all var(--t-fast);
    font-size: var(--fs-2);
    font-weight: var(--fw-medium);
}

.btn-delete:hover {
    background: var(--color-error-dark);
    border-color: var(--color-error-dark);
}

.schedule-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 1rem;
}

.schedule-header h4 {
    margin: 0;
    color: var(--text-dark-primary);
    font-size: var(--fs-3);
    font-weight: var(--fw-semibold);
}

.schedule-header i {
    color: var(--color-primary-500);
    font-size: var(--fs-4);
}

.schedule-summary {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
}

.summary-item {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.5rem 0;
}

.summary-item i {
    width: 20px;
    height: 20px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--color-primary-500);
    font-size: var(--fs-3);
}

.summary-item span {
    font-size: var(--fs-2);
    color: var(--text-dark-primary);
    font-weight: var(--fw-medium);
}

/* Modal Styles */
.schedule-modal {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
    padding: 2rem;
}

.modal-content {
    background: var(--color-neutral-50);
    border-radius: 16px;
    box-shadow: var(--shadow-xl);
    max-width: 500px;
    width: 100%;
    max-height: 80vh;
    overflow-y: auto;
}

.modal-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1.5rem;
    border-bottom: 1px solid var(--color-neutral-200);
}

.modal-header h3 {
    margin: 0;
    color: var(--text-dark-primary);
    font-size: var(--fs-4);
    font-weight: var(--fw-semibold);
}

.modal-close {
    width: 32px;
    height: 32px;
    border-radius: 8px;
    background: var(--color-neutral-200);
    color: var(--text-dark-primary);
    border: none;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all var(--t-fast);
}

.modal-body {
    padding: 1.5rem;
}

.detail-section {
    margin-bottom: 1.5rem;
}

.detail-section:last-child {
    margin-bottom: 0;
}

.detail-section h4 {
    margin: 0 0 1rem 0;
    color: var(--text-dark-primary);
    font-size: var(--fs-3);
    font-weight: var(--fw-semibold);
}

.detail-item {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 0.75rem 0;
    border-bottom: 1px solid var(--color-neutral-100);
}

.detail-item:last-child {
    border-bottom: none;
}

.detail-item i {
    width: 24px;
    height: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--color-primary-500);
    font-size: var(--fs-4);
}

.detail-content {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
}

.detail-label {
    font-size: var(--fs-1);
    color: var(--text-dark-tertiary);
    font-weight: var(--fw-medium);
}

.detail-value {
    font-size: var(--fs-2);
    color: var(--text-dark-primary);
    font-weight: var(--fw-semibold);
}

.webpage-header {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    cursor: pointer;
}

.webpage-actions {
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.dropdown-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 32px;
    height: 32px;
    border-radius: 8px;
    background: var(--color-neutral-200);
    color: var(--text-dark-primary);
    border: none;
    cursor: pointer;
    transition: all var(--t-fast);
    flex-shrink: 0;
}

.webpage-icon {
    width: 40px;
    height: 40px;
    background: var(--color-neutral-100);
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}

.webpage-icon i {
    font-size: var(--fs-4);
    color: var(--color-neutral-600);
}

.webpage-details {
    flex: 1;
    min-width: 0;
}

.webpage-details h3 {
    margin: 0 0 0.25rem 0;
    color: var(--text-dark-primary);
    font-size: var(--fs-3);
    font-weight: var(--fw-semibold);
    line-height: 1.3;
}

.webpage-details .webpage-url {
    margin: 0;
    color: var(--text-dark-secondary);
    font-size: var(--fs-2);
    word-break: break-all;
    line-height: 1.4;
}

.clear-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 40px;
    height: 40px;
    border-radius: 10px;
    background: var(--color-error-light);
    color: var(--color-error);
    border: 1px solid var(--color-error);
    cursor: pointer;
    transition: all var(--t-fast);
    flex-shrink: 0;
}

.schedule-info-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
    margin-bottom: 1rem;
}

.time-info, .day-info {
    background: var(--color-neutral-50);
    border: 1px solid var(--color-neutral-200);
    border-radius: 12px;
    padding: 1rem;
    box-shadow: var(--shadow-sm);
}

.time-info, .day-info {
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.time-info i, .day-info i {
    color: var(--color-primary-500);
    font-size: var(--fs-3);
}

.info-label {
    color: var(--text-dark-tertiary);
    font-size: var(--fs-1);
    font-weight: var(--fw-medium);
}

.info-value {
    color: var(--text-dark-primary);
    font-size: var(--fs-2);
    font-weight: var(--fw-semibold);
}

.scheduling-form {
    background: var(--color-neutral-50);
    border: 1px solid var(--color-neutral-200);
    border-radius: 16px;
    padding: 1.5rem;
}

.scheduling-form h4 {
    margin: 0 0 0.5rem 0;
    color: var(--text-dark-primary);
    font-size: var(--fs-3);
    font-weight: var(--fw-semibold);
}

.form-description {
    margin: 0 0 1.5rem 0;
    color: var(--text-dark-secondary);
    font-size: var(--fs-2);
    line-height: 1.5;
}

.form-placeholder {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 1rem;
    background: var(--color-neutral-100);
    border: 1px dashed var(--color-neutral-300);
    border-radius: 12px;
    color: var(--text-dark-tertiary);
    font-style: italic;
}

.form-placeholder i {
    font-size: var(--fs-4);
    color: var(--color-primary-400);
}


.no-selection {
    text-align: center;
    color: var(--text-dark-tertiary);
    font-style: italic;
    padding: 2rem 0;
}

/* Override global button hover effects for scheduler components */
.schedule-btn:hover {
    background: var(--color-primary-500) !important;
    box-shadow: none !important;
    transform: none !important;
}

.schedule-btn:disabled {
    background: var(--color-neutral-300) !important;
    color: var(--text-dark-tertiary) !important;
    cursor: not-allowed !important;
    opacity: 0.6;
}

.schedule-btn:disabled:hover {
    background: var(--color-neutral-300) !important;
    transform: none !important;
    box-shadow: none !important;
}

.clear-btn:hover {
    background: var(--color-neutral-200) !important;
    box-shadow: none !important;
    transform: none !important;
}

/* Disable all hover effects for scheduler tab components */
.scheduler-view .card:hover {
    box-shadow: var(--shadow-sm) !important;
    transform: none !important;
    border-color: var(--color-neutral-200) !important;
}

.scheduler-view .list-entry:hover {
    background: var(--color-neutral-100) !important;
    border-color: var(--color-neutral-200) !important;
    box-shadow: var(--shadow-xs) !important;
    transform: none !important;
}

.scheduler-view .list-entry:hover .controls {
    opacity: 0 !important;
}
</style>
