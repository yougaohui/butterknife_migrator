package xfkj.fitpro.fragment.base;

import com.blankj.utilcode.util.ActivityUtils;
import com.blankj.utilcode.util.ToastUtils;

import io.reactivex.Observer;
import io.reactivex.disposables.Disposable;
import xfkj.fitpro.R;
import xfkj.fitpro.activity.clockDial.WatchThemeH5Activity;
import xfkj.fitpro.activity.clockDial.WatchThemeHelper;
import xfkj.fitpro.activity.clockDial.watchTheme1.ClockDialListActivity;
import xfkj.fitpro.activity.clockDial.watchTheme2.WatchTheme2Activity;
import xfkj.fitpro.api.HttpHelper;
import xfkj.fitpro.base.NewBaseFragment;
import xfkj.fitpro.bluetooth.SDKCmdMannager;
import xfkj.fitpro.db.DBHelper;
import xfkj.fitpro.event.ClockDialInfoEvent;
import xfkj.fitpro.event.ShowClockDialEvent;
import xfkj.fitpro.model.sever.body.ClockDialInfoBody;
import xfkj.fitpro.model.sever.reponse.BaseResponse;
import xfkj.fitpro.utils.DialogHelper;

public abstract class TabBaseFragment extends NewBaseFragment {
    private final String h5Url = "http://watch.jusonsmart.com";

    @Override
    public void onMessageEvent(Object event) {
        if (event instanceof ClockDialInfoEvent) {
            DialogHelper.hideDialog();
            ClockDialInfoEvent clockDialInfoEvent = (ClockDialInfoEvent) event;
            if (clockDialInfoEvent.getBody() == null) {
                ToastUtils.showShort(clockDialInfoEvent.getErrorInfo());
            } else if (getDelayWhats().contains(R.id.tv_clock_dial_settings)) {
                startWatchTheme();
            }
            stopTimeOut(R.id.tv_clock_dial_settings);
        } else if (event instanceof ShowClockDialEvent) {
            checkShowClockDial();
        }
    }

    protected void checkShowClockDial() {
    }

    protected void enterWatchThemePage() {
        ClockDialInfoBody clockInfo = DBHelper.getClockDialInfo();
        if (null != clockInfo) {
            startWatchTheme();
        } else {
            if (!SDKCmdMannager.getClockDialInfo()) {
                ToastUtils.showShort(R.string.unconnected);
            } else {
                startTimeOut(R.id.tv_clock_dial_settings, 5 * 1000);
                DialogHelper.showDialog(mContext, getString(R.string.query_clock_dial_info), false);
            }
        }
    }

    protected void startWatchTheme() {
        goToLocalWatchTheme();
    }

    /**
     * 进入本地升级表盘页面
     */
    protected void goToLocalWatchTheme() {
        ClockDialInfoBody info = DBHelper.getClockDialInfo();
        if (info != null) {
            if (info.getVersionCode() == 1) {
                ActivityUtils.startActivity(WatchTheme2Activity.class);
            } else {
                ActivityUtils.startActivity(ClockDialListActivity.class);
            }
        }
    }

    protected boolean isChargeWatchThemeAPP() {
        return getResources().getBoolean(R.bool.isChargeWatchThemeAPP);
    }

    /**
     * 进入收费表盘页面
     */
    protected void goToChargeWatchTheme() {
        String params = WatchThemeHelper.getPayH5Params();
        String url = h5Url + "/#/pages/login/index?" + params;
        WatchThemeH5Activity.startH5(mContext, url);
    }

    protected void startCheckChargeWatchTheme() {
        HttpHelper.getInstance().getWatchChargeStatus(new Observer<>() {
            @Override
            public void onSubscribe(Disposable d) {
                DialogHelper.showLoadDialog(mContext);
            }

            @Override
            public void onNext(BaseResponse<String> response) {
                DialogHelper.hideDialog();
                if (response.isSuccess()) {
                    String status = response.getData();
                    if ("1".equals(status) || WatchThemeHelper.isDebugCharge) {//进入收费表盘
                        goToChargeWatchTheme();
                    } else {//进入本地表盘升级
                        goToLocalWatchTheme();
                    }
                } else {
                    ToastUtils.showShort(response.getError().toString());
                }
            }

            @Override
            public void onError(Throwable e) {
                ToastUtils.showShort(e.toString());
                DialogHelper.hideDialog();
            }

            @Override
            public void onComplete() {
                DialogHelper.hideDialog();
            }
        });
    }

    protected ClockDialInfoBody getWatchThemeInfo() {
        return DBHelper.getClockDialInfo();
    }
}
