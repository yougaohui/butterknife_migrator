package xfkj.fitpro.activity;
import static xfkj.fitpro.bluetooth.SendData.getSetInfoByKey;
import android.content.Intent;
import android.content.res.Configuration;
import android.net.Uri;
import android.os.Bundle;
import android.text.SpannableString;
import android.text.Spanned;
import android.text.method.LinkMovementMethod;
import android.text.style.ClickableSpan;
import android.view.View;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.TextView;
import com.blankj.utilcode.util.ActivityUtils;
import com.blankj.utilcode.util.AppUtils;
import com.blankj.utilcode.util.CollectionUtils;
import com.blankj.utilcode.util.ImageUtils;
import com.blankj.utilcode.util.ToastUtils;
import com.umeng.socialize.ShareAction;
import com.umeng.socialize.UMShareAPI;
import com.umeng.socialize.UMShareListener;
import com.umeng.socialize.bean.SHARE_MEDIA;
import com.umeng.socialize.media.UMImage;
import xfkj.fitpro.R;
import xfkj.fitpro.activity.debug.DebugFunctionActivity;
import xfkj.fitpro.base.NewBaseActivity;
import xfkj.fitpro.bluetooth.SDKCmdMannager;
import xfkj.fitpro.db.DBHelper;
import xfkj.fitpro.model.DeviceHardInfoModel;
import xfkj.fitpro.utils.ChannelUtils;
import xfkj.fitpro.utils.Constant;
import xfkj.fitpro.utils.DebugLockHelper;
import xfkj.fitpro.utils.ShareUtils;
public class AboutActivity extends NewBaseActivity {
    LinearLayout mLlAbout;
    TextView mTvVersion;
    TextView mTvLinkProtcol;
    ImageView mImgQrcode;
    Button mBtnShare;
    private ShareAction mShareAction;
    @Override
    public int getLayoutId() {
        return R.layout.activity_about;
    }
    @Override
    public void initData(Bundle savedInstanceState) {
        setTitle(R.string.about);
        //App版本号
        mTvVersion.setText("V " + AppUtils.getAppVersionName());
        mShareAction = new ShareAction(this);
        SHARE_MEDIA[] apps = ShareUtils.getCanShareApps();
        if (CollectionUtils.size(apps) > 0) {
            mShareAction.setDisplayList(apps);
            mShareAction.setShareboardclickCallback((snsPlatform, share_media) ->
                    new ShareAction(AboutActivity.this).
                            withMedia(new UMImage(mContext, ImageUtils.view2Bitmap(mLlAbout)))
                            .setPlatform(share_media)
                            .setCallback(new UMShareListener() {
                                @Override
                                public void onStart(SHARE_MEDIA share_media) {
                                }
                                @Override
                                public void onResult(SHARE_MEDIA share_media) {
                                }
                                @Override
                                public void onError(SHARE_MEDIA share_media, Throwable throwable) {
                                }
                                @Override
                                public void onCancel(SHARE_MEDIA share_media) {
                                }
                            }).share());
        }
    }
    @Override
    public void initListener() {
        mTvVersion.setOnLongClickListener(v -> {
            if (SDKCmdMannager.isConnected()) {
                Constant.mService.commandPoolWrite(getSetInfoByKey((byte) 0x0b), "测试指令");
                ToastUtils.showShort("sendding test cmd");
            } else {
                ToastUtils.showShort(R.string.unconnected);
            }
            return false;
        });
        String userProtcol = "《" + getString(R.string.user_protocol) + "》";
        String privateProtcol = "《" + getString(R.string.private_protocol) + "》";
        SpannableString spanString = new SpannableString(getString(R.string.private_procity_user_protocol, userProtcol, privateProtcol));
        int start1 = spanString.toString().indexOf(userProtcol);
        int end1 = start1 + userProtcol.length();
        spanString.setSpan(new ClickableSpan() {
            @Override
            public void onClick(View view) {
                Intent intent = new Intent(mContext, UserProtocolActivity.class);
                intent.putExtra("isUserProtocol", true);
                ActivityUtils.startActivity(intent);
            }
        }, start1, end1, Spanned.SPAN_MARK_MARK);
        int start2 = spanString.toString().indexOf(privateProtcol);
        int end2 = start2 + privateProtcol.length();
        spanString.setSpan(new ClickableSpan() {
            @Override
            public void onClick(View view) {
                Intent intent = new Intent(mContext, UserProtocolActivity.class);
                intent.putExtra("isUserProtocol", false);
                ActivityUtils.startActivity(intent);
            }
        }, start2, end2, Spanned.SPAN_MARK_MARK);
        mTvLinkProtcol.setText(spanString);
        mTvLinkProtcol.setMovementMethod(LinkMovementMethod.getInstance());//开始响应点击事件
        View tvICP = findViewById(R.id.tv_icp);
        if (null != tvICP) {
            findViewById(R.id.tv_icp).setOnClickListener(v -> {
                Uri uri = Uri.parse("https://beian.miit.gov.cn");
                Intent intent = new Intent(Intent.ACTION_VIEW, uri);
                startActivity(intent);
            });
        }
        mBtnShare.setOnClickListener(v -> {
            if (ChannelUtils.isFitPro()) {
                if (CollectionUtils.size(ShareUtils.getCanShareApps()) > 0) {
                    mShareAction.open(ShareUtils.getShareConfig());
                } else {
                    ToastUtils.showShort(R.string.please_install_can_share_app);
                }
            }else {
                ShareUtils.shareImage(ImageUtils.view2Bitmap(mImgQrcode));
            }
        });
        mBtnShare.setOnLongClickListener(v -> {
            if (DebugLockHelper.getInstance().isDirectEnterDebug()) {
                ActivityUtils.startActivity(DebugFunctionActivity.class);
            } else {
                DebugLockHelper.getInstance().click(() -> startDebugFunctionPage());
            }
            return true;
        });
        
        // 新增的点击事件监听器
        // 初始化点击事件 - 替换@OnClick注解
        findViewById(R.id.tv_link_open_sourece_protcol).setOnClickListener(v -> onMTvLinkOpenSoureceProtcol());

        mImgQrcode.setOnClickListener(v -> onViewLongClicked());

    }
    public void onMTvLinkOpenSoureceProtcol() {
        ActivityUtils.startActivity(UserProtocolActivity.class);
    }
    private void startDebugFunctionPage() {
        ActivityUtils.startActivity(DebugFunctionActivity.class);
        DebugLockHelper.getInstance().passPwd();
    }
    @OnLongClick(R.id.btn_share)
    public void onShareViewLongClicked() {
        Constant.isDebugMode = true;
        ToastUtils.showLong("进入调试模式");
    }
    public void onViewLongClicked() {
        DeviceHardInfoModel hardInfo = DBHelper.getDeviceHardInfo();
        if (hardInfo != null) {
            ToastUtils.showLong(hardInfo.toString());
        } else {
            if (SDKCmdMannager.isConnected()) {
                Constant.mService.commandPoolWrite(getSetInfoByKey((byte) 0x10), "获取硬件信息");
                ToastUtils.showShort("获取失败请重试!");
            } else {
                ToastUtils.showShort(R.string.unconnected);
            }
        }
    }
    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        UMShareAPI.get(this).onActivityResult(requestCode, resultCode, data);
    }
    /**
     * 屏幕横竖屏切换时避免出现window leak的问题
     */
    @Override
    public void onConfigurationChanged(Configuration newConfig) {
        super.onConfigurationChanged(newConfig);
        mShareAction.close();
    }
    @Override
    protected void onDestroy() {
        super.onDestroy();
        mShareAction = null;
    }

    @Override
    protected void initViews() {
        super.initViews();
        // 初始化View绑定 - 替换@BindView注解
        mLlAbout = findViewById(R.id.ll_about);
        mTvVersion = findViewById(R.id.tv_version);
        mTvLinkProtcol = findViewById(R.id.tv_link_protcol);
        mImgQrcode = findViewById(R.id.img_qrcode);
        mBtnShare = findViewById(R.id.btn_share);
    }
}