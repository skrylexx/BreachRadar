import { getRequestConfig } from 'next-intl/server';
import { cookies } from 'next/headers';

export default getRequestConfig(async () => {
  // Try to get the locale from the cookie
  const localeCookie = (await cookies()).get('NEXT_LOCALE')?.value;
  const locale = localeCookie || 'fr'; // default to French since the app is mostly in French

  return {
    locale,
    messages: (await import(`../../messages/${locale}.json`)).default
  };
});
