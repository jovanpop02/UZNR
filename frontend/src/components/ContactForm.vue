<script setup>
import { computed, nextTick, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { submitContactMessage } from '../api'

const { t, locale } = useI18n()

const form = reactive({
  name: '',
  email: '',
  subject: '',
  message: '',
})

// Honeypot. Hidden from people and from screen readers; the API discards any
// submission that arrives with it filled in.
const botField = ref('')

// 'idle' | 'sending' | 'success' | 'error'
const status = ref('idle')
// 'generic' | 'throttled' — which failure message the error alert shows.
const errorKind = ref('generic')
// Errors stay hidden until the first submit attempt, so the form doesn't shout
// at someone who is still filling in the first field.
const submitted = ref(false)
const formEl = ref(null)
const consent = ref(false)

const errors = computed(() => {
  const e = {}
  if (!form.name.trim()) e.name = t('contact.form.errors.name')
  // Deliberately loose: the only check worth making in the browser is that the
  // address has a shape that could deliver. Anything stricter rejects valid
  // addresses.
  if (!/^\S+@\S+\.\S+$/.test(form.email.trim())) e.email = t('contact.form.errors.email')
  if (form.subject.trim().length < 3) e.subject = t('contact.form.errors.subject')
  if (form.message.trim().length < 20) e.message = t('contact.form.errors.message')
  if (!consent.value) e.consent = t('contact.form.errors.consent')
  return e
})

function showError(field) {
  return submitted.value && Boolean(errors.value[field])
}

async function onSubmit() {
  submitted.value = true
  if (Object.keys(errors.value).length) {
    await nextTick()
    formEl.value?.querySelector('[aria-invalid="true"]')?.focus()
    return
  }

  status.value = 'sending'
  errorKind.value = 'generic'
  try {
    await submitContactMessage({
      ...form,
      language: locale.value === 'en' ? 'en' : 'mne',
      website: botField.value,
    })
    status.value = 'success'
  } catch (err) {
    // Being rate-limited is not a failure the visitor can fix by retrying, so
    // it gets its own message.
    errorKind.value = err?.status === 429 ? 'throttled' : 'generic'
    status.value = 'error'
  }
}

function reset() {
  Object.keys(form).forEach((key) => {
    form[key] = ''
  })
  consent.value = false
  submitted.value = false
  status.value = 'idle'
  errorKind.value = 'generic'
}
</script>

<template>
  <div class="cform">
    <div v-if="status === 'success'" class="cform__success" role="status">
      <span class="cform__success-icon" aria-hidden="true">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="m5 12.5 4.5 4.5L19 7.5" stroke-linecap="round" stroke-linejoin="round" />
        </svg>
      </span>
      <h3>{{ t('contact.form.successTitle') }}</h3>
      <p>{{ t('contact.form.successText') }}</p>
      <button type="button" class="btn btn--primary" @click="reset">
        {{ t('contact.form.sendAnother') }}
      </button>
    </div>

    <form v-else ref="formEl" class="cform__form" novalidate @submit.prevent="onSubmit">
      <p class="cform__honeypot" aria-hidden="true">
        <label>Ne popunjavajte ovo polje <input v-model="botField" type="text" name="website" tabindex="-1" autocomplete="off" /></label>
      </p>

      <div class="cform__grid">
        <div class="cform__field">
          <label for="cf-name">{{ t('contact.form.nameLabel') }}</label>
          <input
            id="cf-name"
            v-model="form.name"
            type="text"
            name="name"
            autocomplete="name"
            :placeholder="t('contact.form.namePlaceholder')"
            :aria-invalid="showError('name')"
            :aria-describedby="showError('name') ? 'cf-name-err' : undefined"
          />
          <p v-if="showError('name')" id="cf-name-err" class="cform__error">{{ errors.name }}</p>
        </div>

        <div class="cform__field">
          <label for="cf-email">{{ t('contact.form.emailLabel') }}</label>
          <input
            id="cf-email"
            v-model="form.email"
            type="email"
            name="email"
            autocomplete="email"
            :placeholder="t('contact.form.emailPlaceholder')"
            :aria-invalid="showError('email')"
            :aria-describedby="showError('email') ? 'cf-email-err' : undefined"
          />
          <p v-if="showError('email')" id="cf-email-err" class="cform__error">{{ errors.email }}</p>
        </div>

        <div class="cform__field cform__field--wide">
          <label for="cf-subject">{{ t('contact.form.subjectLabel') }}</label>
          <input
            id="cf-subject"
            v-model="form.subject"
            type="text"
            name="subject"
            :placeholder="t('contact.form.subjectPlaceholder')"
            :aria-invalid="showError('subject')"
            :aria-describedby="showError('subject') ? 'cf-subject-err' : undefined"
          />
          <p v-if="showError('subject')" id="cf-subject-err" class="cform__error">{{ errors.subject }}</p>
        </div>

        <div class="cform__field cform__field--wide">
          <label for="cf-message">{{ t('contact.form.messageLabel') }}</label>
          <textarea
            id="cf-message"
            v-model="form.message"
            name="message"
            rows="6"
            :placeholder="t('contact.form.messagePlaceholder')"
            :aria-invalid="showError('message')"
            :aria-describedby="showError('message') ? 'cf-message-err' : 'cf-message-hint'"
          ></textarea>
          <p v-if="showError('message')" id="cf-message-err" class="cform__error">{{ errors.message }}</p>
          <p v-else id="cf-message-hint" class="cform__hint">{{ t('contact.form.messageHint') }}</p>
        </div>
      </div>

      <label class="cform__consent" :class="{ 'cform__consent--error': showError('consent') }">
        <input
          v-model="consent"
          type="checkbox"
          :aria-invalid="showError('consent')"
          :aria-describedby="showError('consent') ? 'cf-consent-err' : undefined"
        />
        <span>{{ t('contact.form.consentLabel') }}</span>
      </label>
      <p v-if="showError('consent')" id="cf-consent-err" class="cform__error">{{ errors.consent }}</p>

      <div v-if="status === 'error'" class="cform__alert" role="alert">
        <strong>{{ errorKind === 'throttled' ? t('contact.form.throttledTitle') : t('contact.form.errorTitle') }}</strong>
        <span>{{ errorKind === 'throttled' ? t('contact.form.throttledText') : t('contact.form.errorText') }}</span>
      </div>

      <div class="cform__actions">
        <button type="submit" class="btn btn--primary" :disabled="status === 'sending'">
          <svg v-if="status !== 'sending'" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true">
            <path d="M4.5 12 20 4.5 15.5 20l-3.6-6.4L4.5 12Z" stroke-linejoin="round" />
          </svg>
          {{ status === 'sending' ? t('contact.form.sending') : t('contact.form.submit') }}
        </button>
        <p class="cform__note">{{ t('contact.form.privacyNote') }}</p>
      </div>
    </form>
  </div>
</template>

<style scoped>
.cform {
  background: var(--color-card-bg);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--space-5);
  box-shadow: var(--shadow-sm);
}

.cform__honeypot {
  position: absolute;
  width: 1px;
  height: 1px;
  overflow: hidden;
  clip-path: inset(50%);
  white-space: nowrap;
}

.cform__grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: var(--space-4);
}

.cform__field {
  display: flex;
  flex-direction: column;
  gap: 6px;
  min-width: 0;
}

.cform__field--wide {
  grid-column: 1 / -1;
}

.cform__field label {
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--color-ink);
}

.cform__field input,
.cform__field textarea {
  width: 100%;
  padding: 11px var(--space-3);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  background: var(--color-bg);
  font: inherit;
  font-size: 0.95rem;
  color: var(--color-ink);
  transition: border-color 0.15s ease, box-shadow 0.15s ease;
}

.cform__field textarea {
  resize: vertical;
  min-height: 140px;
}

.cform__field input::placeholder,
.cform__field textarea::placeholder {
  color: var(--color-text-muted);
}

.cform__field input:focus,
.cform__field textarea:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px var(--color-primary-light);
}

.cform__field [aria-invalid='true'] {
  border-color: var(--color-danger);
  background: var(--color-danger-light);
}

.cform__field [aria-invalid='true']:focus {
  border-color: var(--color-danger);
  box-shadow: 0 0 0 3px rgba(195, 58, 48, 0.16);
}

.cform__hint,
.cform__error {
  font-size: 0.85rem;
  margin: 0;
}

.cform__hint {
  color: var(--color-text-muted);
}

.cform__error {
  color: var(--color-danger);
  font-weight: 600;
}

.cform__consent {
  display: flex;
  align-items: flex-start;
  gap: var(--space-2);
  margin-top: var(--space-4);
  font-size: 0.9rem;
  color: var(--color-text);
  cursor: pointer;
}

.cform__consent input {
  margin-top: 3px;
  width: 17px;
  height: 17px;
  flex: 0 0 auto;
  accent-color: var(--color-primary);
}

.cform__consent--error span {
  color: var(--color-danger);
}

.cform__alert {
  display: grid;
  gap: 2px;
  margin-top: var(--space-4);
  padding: var(--space-3);
  border: 1px solid var(--color-danger);
  border-radius: var(--radius-sm);
  background: var(--color-danger-light);
  font-size: 0.9rem;
  color: var(--color-text);
}

.cform__alert strong {
  color: var(--color-danger);
}

.cform__actions {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: var(--space-3);
  margin-top: var(--space-5);
}

.cform__actions .btn[disabled] {
  opacity: 0.7;
  cursor: progress;
}

.cform__note {
  font-size: 0.85rem;
  color: var(--color-text-muted);
  margin: 0;
}

.cform__success {
  display: grid;
  justify-items: start;
  gap: var(--space-2);
  padding: var(--space-4) 0;
}

.cform__success-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  border-radius: 999px;
  background: var(--color-primary-light);
  color: var(--color-primary);
  margin-bottom: var(--space-2);
}

.cform__success-icon svg {
  width: 26px;
  height: 26px;
}

.cform__success p {
  color: var(--color-text-muted);
  max-width: 52ch;
}

.cform__success .btn {
  margin-top: var(--space-3);
}

@media (max-width: 700px) {
  .cform {
    padding: var(--space-4);
  }

  .cform__grid {
    grid-template-columns: 1fr;
  }
}
</style>
