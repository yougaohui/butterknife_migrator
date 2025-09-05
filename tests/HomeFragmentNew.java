package xfkj.fitpro.fragment;
import android.content.res.Configuration;
import android.graphics.Color;
import android.graphics.Point;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.FrameLayout;
import android.widget.LinearLayout;
import com.unad.sdk.UNADBannerAdLoader;
import com.unad.sdk.dto.UnadError;
import xfkj.fitpro.R;
import xfkj.fitpro.fragment.base.HomeBaseFragment;
import xfkj.fitpro.utils.CommonUtils;
import xfkj.fitpro.utils.adv.DownloadConfirmHelper;
/**
 * 新的首页界面
 */
public class HomeFragmentNew extends HomeBaseFragment {
    @Override
    public void initData(Bundle savedInstanceState) {
        super.initData(savedInstanceState);
        //刷新banner广告
        refreshBanner();
    }
    /*Banner广告相关开始*/
    FrameLayout bannerContainer;
    private UNADBannerAdLoader banner;
    private void loadBanner() {
        if (!CommonUtils.isShowAdv()) return;
        //正式环境请替换正式ID
        String splashAdId = "Adgo-unit-1569484795";
        banner = new UNADBannerAdLoader(getActivity(), splashAdId, bannerContainer,
                new UNADBannerAdLoader.UNADBannerADListener() {
                    @Override
                    public void onADError(UnadError error) {
                        Log.e(TAG, "onADError:" + error.getMessage());
                        stopBanner();
                    }
                    @Override
                    public void onADReceive() {
                        Log.e(TAG, "onADReceive");
                    }
                    @Override
                    public void onADPresent() {
                        Log.e(TAG, "onADPresent");
                        bannerContainer.setBackgroundColor(Color.WHITE);
                    }
                    @Override
                    public void onADClosed() {
                        Log.e(TAG, "onADClosed");
                        stopBanner();
                    }
                    @Override
                    public void onADClicked() {
                        Log.e(TAG, "onADClicked");
                    }
                });
        //用户自定义下载
        //用户自定义下载
        banner.setDownloadConfirmListener(DownloadConfirmHelper.DOWNLOAD_CONFIRM_LISTENER);
        // 合法取值:0(不轮播)和[30,120].单位:秒
        banner.setRefreshTime(30);
        banner.load();
    }
    @Override
    public void onConfigurationChanged(Configuration newConfig) {
        super.onConfigurationChanged(newConfig);
        if (bannerContainer != null) {
            bannerContainer.setLayoutParams(getUnifiedBannerLayoutParams());
        }
    }
    private LinearLayout.LayoutParams getUnifiedBannerLayoutParams() {
        Point screenSize = new Point();
        getActivity().getWindowManager().getDefaultDisplay().getSize(screenSize);
        return new LinearLayout.LayoutParams(screenSize.x, Math.round(screenSize.x / 6.4F));
    }
    public void refreshBanner() {
        loadBanner();
        bannerContainer.setVisibility(View.VISIBLE);
    }
    public void stopBanner() {
        if (null != banner) {
            banner.destroy();
            if (bannerContainer != null) {
                bannerContainer.setVisibility(View.GONE);
            }
        }
    }
    @Override
    public void onDestroy() {
        super.onDestroy();
        if (null != banner) {
            banner.destroy();
        }
    }
    /*banner广告结束*/

    @Override
    protected void initViews() {
        super.initViews();
        // 初始化View绑定 - 替换@BindView注解
        bannerContainer = findViewById(R.id.bannerContainer);
    }
}